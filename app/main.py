from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Import models dan services
from app.database import get_db, init_db
from app.models import Tweet, TwitterUser, HoaxAnalysis, AnalysisSession
from app.services.twitter_service import TwitterService
from app.services.openai_service import OpenAIService
from app.services.brave_search_service import BraveSearchService
from app.services.bot_detection_service import BotDetectionService
from app.services.network_analysis_service import NetworkAnalysisService
from app.services.pdf_service import PDFService
from app.config import config

# Setup FastAPI app
app = FastAPI(
    title="Twitter Hoax Detector",
    description="Sistem deteksi hoax pada platform Twitter",
    version="1.0.0"
)

# Setup static files dan templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")
app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")

templates = Jinja2Templates(directory="templates")

# Initialize services
twitter_service = TwitterService(use_real_api=False)  # Set True untuk API asli
openai_service = OpenAIService()
brave_search_service = BraveSearchService(use_real_api=False)  # Set True untuk API asli
bot_detection_service = BotDetectionService()
network_analysis_service = NetworkAnalysisService()
pdf_service = PDFService()

# Buat direktori yang diperlukan
os.makedirs("reports", exist_ok=True)
os.makedirs("visualizations", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Initialize database
init_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard utama"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    """Halaman analisis"""
    return templates.TemplateResponse("analyze.html", {"request": request})

@app.post("/api/analyze")
async def analyze_tweet(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Endpoint untuk analisis tweet"""
    try:
        # Ambil data dari request
        form_data = await request.form()
        tweet_url = form_data.get("tweet_url")
        
        if not tweet_url:
            raise HTTPException(status_code=400, detail="URL tweet harus diisi")
        
        # Buat session ID
        session_id = str(uuid.uuid4())
        
        # Buat analysis session
        analysis_session = AnalysisSession(
            session_id=session_id,
            tweet_url=tweet_url,
            user_ip=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            status="processing",
            progress=0
        )
        
        db.add(analysis_session)
        db.commit()
        
        # Jalankan analisis di background
        background_tasks.add_task(
            run_full_analysis,
            session_id,
            tweet_url,
            db
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Analisis dimulai. Gunakan session_id untuk cek status."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{session_id}")
async def get_analysis_status(session_id: str, db: Session = Depends(get_db)):
    """Cek status analisis"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")
    
    return {
        "session_id": session_id,
        "status": session.status,
        "progress": session.progress,
        "error_message": session.error_message,
        "created_at": session.created_at
    }

@app.get("/api/result/{session_id}")
async def get_analysis_result(session_id: str, db: Session = Depends(get_db)):
    """Dapatkan hasil analisis"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Analisis belum selesai")
    
    # Ambil hasil analisis
    if session.analysis_id:
        analysis = db.query(HoaxAnalysis).filter(
            HoaxAnalysis.id == session.analysis_id
        ).first()
        
        if analysis:
            tweet = db.query(Tweet).filter(
                Tweet.tweet_id == analysis.tweet_id
            ).first()
            
            user = db.query(TwitterUser).filter(
                TwitterUser.user_id == tweet.user_id
            ).first() if tweet else None
            
            return {
                "session_id": session_id,
                "tweet_data": {
                    "tweet_id": tweet.tweet_id if tweet else None,
                    "text": tweet.text if tweet else None,
                    "url": tweet.url if tweet else None,
                    "created_at": tweet.created_at_twitter if tweet else None,
                    "retweet_count": tweet.retweet_count if tweet else 0,
                    "like_count": tweet.like_count if tweet else 0,
                    "reply_count": tweet.reply_count if tweet else 0,
                    "user": {
                        "username": user.username if user else None,
                        "display_name": user.display_name if user else None,
                        "followers_count": user.followers_count if user else 0,
                        "verified": user.verified if user else False
                    } if user else None
                },
                "hoax_analysis": {
                    "hoax_probability": analysis.hoax_probability,
                    "is_hoax": analysis.is_hoax,
                    "hoax_reasons": analysis.hoax_reasons,
                    "openai_analysis": analysis.openai_analysis
                },
                "bot_detection": {
                    "bot_probability": user.bot_probability if user else 0,
                    "is_bot": user.is_bot if user else False
                },
                "fact_check_results": analysis.fact_check_results,
                "network_data": analysis.network_data,
                "pdf_report_path": analysis.pdf_report_path,
                "network_visualization_path": analysis.network_visualization_path
            }
    
    raise HTTPException(status_code=404, detail="Hasil analisis tidak ditemukan")

@app.get("/api/download/pdf/{session_id}")
async def download_pdf_report(session_id: str, db: Session = Depends(get_db)):
    """Download laporan PDF"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session or session.status != "completed":
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    
    if session.analysis_id:
        analysis = db.query(HoaxAnalysis).filter(
            HoaxAnalysis.id == session.analysis_id
        ).first()
        
        if analysis and analysis.pdf_report_path and os.path.exists(analysis.pdf_report_path):
            return FileResponse(
                analysis.pdf_report_path,
                media_type="application/pdf",
                filename=f"hoax_analysis_{session_id}.pdf"
            )
    
    raise HTTPException(status_code=404, detail="File PDF tidak ditemukan")

@app.get("/api/visualization/{session_id}")
async def get_network_visualization(session_id: str, db: Session = Depends(get_db)):
    """Dapatkan visualisasi jaringan"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session or session.status != "completed":
        raise HTTPException(status_code=404, detail="Visualisasi tidak ditemukan")
    
    if session.analysis_id:
        analysis = db.query(HoaxAnalysis).filter(
            HoaxAnalysis.id == session.analysis_id
        ).first()
        
        if analysis and analysis.network_visualization_path:
            return {"visualization_path": analysis.network_visualization_path}
    
    raise HTTPException(status_code=404, detail="Visualisasi tidak ditemukan")

@app.get("/visualization/view/{session_id}")
async def view_network_visualization(session_id: str, db: Session = Depends(get_db)):
    """Lihat visualisasi jaringan secara langsung"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session or session.status != "completed":
        raise HTTPException(status_code=404, detail="Visualisasi tidak ditemukan")
    
    if session.analysis_id:
        analysis = db.query(HoaxAnalysis).filter(
            HoaxAnalysis.id == session.analysis_id
        ).first()
        
        if analysis and analysis.network_visualization_path:
            file_path = analysis.network_visualization_path
            if os.path.exists(file_path):
                return FileResponse(
                    file_path,
                    media_type="text/html",
                    filename=f"network_visualization_{session_id}.html"
                )
    
    raise HTTPException(status_code=404, detail="File visualisasi tidak ditemukan")

@app.get("/influence/view/{session_id}")
async def view_influence_chart(session_id: str, db: Session = Depends(get_db)):
    """Lihat chart pengaruh secara langsung"""
    
    session = db.query(AnalysisSession).filter(
        AnalysisSession.session_id == session_id
    ).first()
    
    if not session or session.status != "completed":
        raise HTTPException(status_code=404, detail="Chart tidak ditemukan")
    
    if session.analysis_id:
        analysis = db.query(HoaxAnalysis).filter(
            HoaxAnalysis.id == session.analysis_id
        ).first()
        
        if analysis and analysis.network_data:
            # Generate influence chart on-the-fly
            network_data = analysis.network_data
            network_analysis_result = network_analysis_service.analyze_network(network_data)
            influential_nodes = network_analysis_result.get('influential_nodes', [])
            
            if influential_nodes:
                chart_path = network_analysis_service.create_influence_chart(influential_nodes)
                if os.path.exists(chart_path):
                    return FileResponse(
                        chart_path,
                        media_type="text/html",
                        filename=f"influence_chart_{session_id}.html"
                    )
    
    raise HTTPException(status_code=404, detail="File chart tidak ditemukan")

@app.get("/api/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Dapatkan statistik sistem"""
    
    # Statistik dasar
    total_analyses = db.query(HoaxAnalysis).count()
    hoax_count = db.query(HoaxAnalysis).filter(HoaxAnalysis.is_hoax == True).count()
    bot_count = db.query(TwitterUser).filter(TwitterUser.is_bot == True).count()
    total_users = db.query(TwitterUser).count()
    
    # Statistik bulanan
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_analyses = db.query(HoaxAnalysis).filter(
        HoaxAnalysis.created_at >= thirty_days_ago
    ).count()
    
    return {
        "total_analyses": total_analyses,
        "hoax_count": hoax_count,
        "hoax_percentage": round((hoax_count / total_analyses * 100), 1) if total_analyses > 0 else 0,
        "bot_count": bot_count,
        "bot_percentage": round((bot_count / total_users * 100), 1) if total_users > 0 else 0,
        "recent_analyses": recent_analyses,
        "total_users": total_users
    }

@app.get("/result/{session_id}", response_class=HTMLResponse)
async def result_page(request: Request, session_id: str):
    """Halaman hasil analisis"""
    return templates.TemplateResponse("result.html", {
        "request": request,
        "session_id": session_id
    })

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Halaman riwayat analisis"""
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/api/history")
async def get_analysis_history(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Dapatkan riwayat analisis"""
    
    offset = (page - 1) * limit
    
    sessions = db.query(AnalysisSession).filter(
        AnalysisSession.status == "completed"
    ).order_by(AnalysisSession.created_at.desc()).offset(offset).limit(limit).all()
    
    history = []
    for session in sessions:
        if session.analysis_id:
            analysis = db.query(HoaxAnalysis).filter(
                HoaxAnalysis.id == session.analysis_id
            ).first()
            
            if analysis:
                tweet = db.query(Tweet).filter(
                    Tweet.tweet_id == analysis.tweet_id
                ).first()
                
                history.append({
                    "session_id": session.session_id,
                    "tweet_url": session.tweet_url,
                    "tweet_text": tweet.text[:100] + "..." if tweet and tweet.text else "",
                    "is_hoax": analysis.is_hoax,
                    "hoax_probability": analysis.hoax_probability,
                    "created_at": session.created_at
                })
    
    total_count = db.query(AnalysisSession).filter(
        AnalysisSession.status == "completed"
    ).count()
    
    return {
        "history": history,
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

async def run_full_analysis(session_id: str, tweet_url: str, db: Session):
    """Jalankan analisis lengkap"""
    
    try:
        # Update status
        session = db.query(AnalysisSession).filter(
            AnalysisSession.session_id == session_id
        ).first()
        
        if not session:
            return
        
        session.status = "processing"
        session.progress = 10
        db.commit()
        
        # 1. Ekstrak data tweet
        tweet_data = twitter_service.get_tweet_data(tweet_url)
        session.progress = 20
        db.commit()
        
        # 2. Simpan data user
        user_data = tweet_data.get('user', {})
        user = db.query(TwitterUser).filter(
            TwitterUser.user_id == user_data.get('user_id')
        ).first()
        
        if not user:
            user = TwitterUser(
                user_id=user_data.get('user_id'),
                username=user_data.get('username'),
                display_name=user_data.get('display_name'),
                bio=user_data.get('bio'),
                followers_count=user_data.get('followers_count', 0),
                following_count=user_data.get('following_count', 0),
                tweet_count=user_data.get('tweet_count', 0),
                verified=user_data.get('verified', False),
                profile_image_url=user_data.get('profile_image_url'),
                account_creation_date=user_data.get('account_creation_date')
            )
            db.add(user)
            db.commit()
        
        # 3. Simpan data tweet
        tweet = db.query(Tweet).filter(
            Tweet.tweet_id == tweet_data.get('tweet_id')
        ).first()
        
        if not tweet:
            tweet = Tweet(
                tweet_id=tweet_data.get('tweet_id'),
                url=tweet_url,
                text=tweet_data.get('text'),
                created_at_twitter=tweet_data.get('created_at'),
                retweet_count=tweet_data.get('retweet_count', 0),
                like_count=tweet_data.get('like_count', 0),
                reply_count=tweet_data.get('reply_count', 0),
                quote_count=tweet_data.get('quote_count', 0),
                user_id=user_data.get('user_id')
            )
            db.add(tweet)
            db.commit()
        
        session.progress = 30
        db.commit()
        
        # 4. Analisis hoax dengan OpenAI
        hoax_analysis = openai_service.analyze_hoax(tweet_data.get('text', ''), user_data)
        session.progress = 50
        db.commit()
        
        # 5. Deteksi bot
        bot_analysis = bot_detection_service.detect_bot(user_data)
        
        # Update user dengan hasil bot detection
        user.bot_probability = bot_analysis.get('bot_probability', 0)
        user.is_bot = bot_analysis.get('is_bot', False)
        user.bot_detection_date = datetime.utcnow()
        db.commit()
        
        session.progress = 60
        db.commit()
        
        # 6. Fact-checking dengan Brave Search
        search_query = f"fact check {tweet_data.get('text', '')[:100]}"
        fact_check_results = brave_search_service.search_for_fact_check(search_query, tweet_data.get('text', ''))
        session.progress = 70
        db.commit()
        
        # 7. Analisis jaringan
        network_data = twitter_service.get_tweet_network_data(tweet_data.get('tweet_id'))
        network_analysis = network_analysis_service.analyze_network(network_data)
        session.progress = 80
        db.commit()
        
        # 8. Buat visualisasi jaringan
        visualization_path = network_analysis_service.create_network_visualization()
        
        # 8.1. Buat influence chart
        influential_nodes = network_analysis.get('influential_nodes', [])
        influence_chart_path = ""
        if influential_nodes:
            influence_chart_path = network_analysis_service.create_influence_chart(influential_nodes)
        
        session.progress = 85
        db.commit()
        
        # 9. Generate laporan PDF
        analysis_data = {
            'tweet_url': tweet_url,
            'tweet_data': tweet_data,
            'hoax_analysis': hoax_analysis,
            'bot_detection': bot_analysis,
            'fact_check_results': fact_check_results,
            'network_analysis': network_analysis
        }
        
        pdf_path = pdf_service.generate_hoax_report(analysis_data)
        session.progress = 95
        db.commit()
        
        # 10. Simpan hasil analisis
        analysis = HoaxAnalysis(
            tweet_id=tweet_data.get('tweet_id'),
            openai_analysis=hoax_analysis.get('raw_analysis', ''),
            hoax_probability=hoax_analysis.get('hoax_probability', 0),
            is_hoax=hoax_analysis.get('is_hoax', False),
            hoax_reasons=hoax_analysis.get('reasons', []),
            fact_check_results=fact_check_results,
            network_data=network_data,
            influence_score=network_analysis.get('total_interactions', 0),
            network_visualization_path=visualization_path,
            influence_chart_path=influence_chart_path,
            pdf_report_path=pdf_path
        )
        
        db.add(analysis)
        db.commit()
        
        # Update session dengan hasil
        session.analysis_id = analysis.id
        session.status = "completed"
        session.progress = 100
        db.commit()
        
    except Exception as e:
        # Update session dengan error
        session.status = "failed"
        session.error_message = str(e)
        db.commit()
        print(f"Error in analysis: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=config.DEBUG) 