import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime

class NetworkAnalysisService:
    """Service untuk analisis jaringan penyebaran tweet"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.pos = None
        
    def analyze_network(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisis jaringan penyebaran tweet"""
        
        # Buat graf dari data
        self.graph = self._create_graph(network_data)
        
        # Hitung metrik jaringan
        metrics = self._calculate_network_metrics()
        
        # Identifikasi node penting
        influential_nodes = self._identify_influential_nodes()
        
        # Deteksi komunitas
        communities = self._detect_communities()
        
        # Analisis pola penyebaran
        spread_patterns = self._analyze_spread_patterns()
        
        return {
            'network_metrics': metrics,
            'influential_nodes': influential_nodes,
            'communities': communities,
            'spread_patterns': spread_patterns,
            'graph_data': network_data,
            'total_nodes': len(self.graph.nodes()),
            'total_edges': len(self.graph.edges())
        }
    
    def _create_graph(self, network_data: Dict[str, Any]) -> nx.DiGraph:
        """Buat graf dari data jaringan"""
        graph = nx.DiGraph()
        
        # Tambahkan nodes
        for node in network_data.get('nodes', []):
            graph.add_node(
                node['id'],
                label=node.get('label', ''),
                type=node.get('type', 'user'),
                followers=node.get('followers', 0),
                influence_score=node.get('influence_score', 0.0)
            )
        
        # Tambahkan edges
        for edge in network_data.get('edges', []):
            graph.add_edge(
                edge['from'],
                edge['to'],
                type=edge.get('type', 'interaction'),
                weight=edge.get('weight', 1.0)
            )
        
        return graph
    
    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Hitung metrik jaringan"""
        if len(self.graph.nodes()) == 0:
            return {}
        
        # Metrik dasar
        num_nodes = len(self.graph.nodes())
        num_edges = len(self.graph.edges())
        density = nx.density(self.graph)
        
        # Centrality measures
        centrality_measures = {}
        try:
            centrality_measures['degree'] = nx.degree_centrality(self.graph)
            centrality_measures['betweenness'] = nx.betweenness_centrality(self.graph)
            centrality_measures['closeness'] = nx.closeness_centrality(self.graph)
            centrality_measures['pagerank'] = nx.pagerank(self.graph)
        except:
            centrality_measures = {}
        
        # Komponen terhubung
        num_components = nx.number_weakly_connected_components(self.graph)
        largest_component_size = len(max(nx.weakly_connected_components(self.graph), key=len, default=[]))
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'density': round(density, 3),
            'num_components': num_components,
            'largest_component_size': largest_component_size,
            'centrality_measures': centrality_measures,
            'avg_degree': round(sum(dict(self.graph.degree()).values()) / num_nodes, 2) if num_nodes > 0 else 0
        }
    
    def _identify_influential_nodes(self) -> List[Dict[str, Any]]:
        """Identifikasi node yang paling berpengaruh"""
        if len(self.graph.nodes()) == 0:
            return []
        
        influential_nodes = []
        
        try:
            # Hitung PageRank
            pagerank = nx.pagerank(self.graph)
            
            # Hitung degree centrality
            degree_centrality = nx.degree_centrality(self.graph)
            
            # Kombinasi skor
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                influence_score = (
                    pagerank.get(node, 0) * 0.4 +
                    degree_centrality.get(node, 0) * 0.3 +
                    node_data.get('influence_score', 0) * 0.3
                )
                
                influential_nodes.append({
                    'node_id': node,
                    'label': node_data.get('label', node),
                    'type': node_data.get('type', 'user'),
                    'followers': node_data.get('followers', 0),
                    'influence_score': round(influence_score, 3),
                    'pagerank': round(pagerank.get(node, 0), 3),
                    'degree_centrality': round(degree_centrality.get(node, 0), 3)
                })
        except:
            # Fallback jika ada error
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                influential_nodes.append({
                    'node_id': node,
                    'label': node_data.get('label', node),
                    'type': node_data.get('type', 'user'),
                    'followers': node_data.get('followers', 0),
                    'influence_score': node_data.get('influence_score', 0),
                    'pagerank': 0,
                    'degree_centrality': 0
                })
        
        # Urutkan berdasarkan influence score
        influential_nodes.sort(key=lambda x: x['influence_score'], reverse=True)
        
        return influential_nodes[:10]  # Top 10 most influential
    
    def _detect_communities(self) -> Dict[str, Any]:
        """Deteksi komunitas dalam jaringan"""
        if len(self.graph.nodes()) < 3:
            return {'communities': [], 'modularity': 0}
        
        try:
            # Konversi ke undirected graph untuk community detection
            undirected_graph = self.graph.to_undirected()
            
            # Gunakan algoritma Louvain (try multiple methods)
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(undirected_graph)
            except ImportError:
                try:
                    from networkx.algorithms import community as nx_community
                    communities_generator = nx_community.greedy_modularity_communities(undirected_graph)
                    partition = {}
                    for i, community in enumerate(communities_generator):
                        for node in community:
                            partition[node] = i
                except:
                    # Simple fallback: create single community
                    partition = {node: 0 for node in undirected_graph.nodes()}
            
            # Hitung modularity
            try:
                modularity = community_louvain.modularity(partition, undirected_graph)
            except:
                try:
                    modularity = nx.algorithms.community.modularity(undirected_graph, 
                        [set(nodes) for nodes in communities_generator])
                except:
                    modularity = 0.0
            
            # Kelompokkan nodes berdasarkan komunitas
            communities = {}
            for node, comm_id in partition.items():
                if comm_id not in communities:
                    communities[comm_id] = []
                communities[comm_id].append(node)
            
            # Format hasil
            community_list = []
            for comm_id, nodes in communities.items():
                community_list.append({
                    'community_id': comm_id,
                    'nodes': nodes,
                    'size': len(nodes),
                    'density': self._calculate_community_density(nodes)
                })
            
            return {
                'communities': community_list,
                'modularity': round(modularity, 3),
                'num_communities': len(community_list)
            }
            
        except Exception as e:
            print(f"Error in community detection: {e}")
            return {'communities': [], 'modularity': 0, 'num_communities': 0}
    
    def _calculate_community_density(self, nodes: List[str]) -> float:
        """Hitung densitas komunitas"""
        if len(nodes) < 2:
            return 0.0
        
        subgraph = self.graph.subgraph(nodes)
        return nx.density(subgraph)
    
    def _analyze_spread_patterns(self) -> Dict[str, Any]:
        """Analisis pola penyebaran"""
        patterns = {
            'viral_potential': self._calculate_viral_potential(),
            'echo_chamber_score': self._calculate_echo_chamber_score(),
            'bot_influence': self._calculate_bot_influence(),
            'spread_velocity': self._calculate_spread_velocity()
        }
        
        return patterns
    
    def _calculate_viral_potential(self) -> float:
        """Hitung potensi viral berdasarkan struktur jaringan"""
        if len(self.graph.nodes()) == 0:
            return 0.0
        
        # Faktor: jumlah retweet, diversitas follower, centrality
        retweet_count = sum(1 for _, _, data in self.graph.edges(data=True) if data.get('type') == 'retweet')
        total_followers = sum(data.get('followers', 0) for _, data in self.graph.nodes(data=True))
        
        # Normalisasi
        viral_score = min((retweet_count * 0.3 + total_followers * 0.0001) / 10, 1.0)
        
        return round(viral_score, 3)
    
    def _calculate_echo_chamber_score(self) -> float:
        """Hitung skor echo chamber"""
        if len(self.graph.nodes()) < 3:
            return 0.0
        
        # Hitung clustering coefficient
        try:
            clustering = nx.average_clustering(self.graph.to_undirected())
            return round(clustering, 3)
        except:
            return 0.0
    
    def _calculate_bot_influence(self) -> float:
        """Hitung pengaruh bot dalam jaringan"""
        if len(self.graph.nodes()) == 0:
            return 0.0
        
        # Asumsi: node dengan influence_score rendah adalah bot
        bot_nodes = [node for node, data in self.graph.nodes(data=True) 
                    if data.get('influence_score', 0) < 0.3]
        
        bot_influence = len(bot_nodes) / len(self.graph.nodes())
        return round(bot_influence, 3)
    
    def _calculate_spread_velocity(self) -> float:
        """Hitung kecepatan penyebaran"""
        # Simplified: berdasarkan jumlah edge dan struktur
        if len(self.graph.edges()) == 0:
            return 0.0
        
        velocity = len(self.graph.edges()) / len(self.graph.nodes()) if len(self.graph.nodes()) > 0 else 0
        return round(min(velocity, 10.0), 3)
    
    def create_network_visualization(self, output_path: str = None) -> str:
        """Buat visualisasi jaringan menggunakan Plotly"""
        if len(self.graph.nodes()) == 0:
            return ""
        
        # Buat layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Persiapkan data untuk Plotly
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Node info
            node_data = self.graph.nodes[node]
            node_text.append(f"{node_data.get('label', node)}<br>Followers: {node_data.get('followers', 0)}")
            
            # Color berdasarkan type
            node_type = node_data.get('type', 'user')
            if node_type == 'original':
                node_color.append('red')
                node_size.append(20)
            elif node_type == 'retweet':
                node_color.append('blue')
                node_size.append(15)
            elif node_type == 'reply':
                node_color.append('green')
                node_size.append(12)
            else:
                node_color.append('orange')
                node_size.append(10)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2)
            )
        )
        
        # Buat figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Network Analysis - Tweet Spread',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Red: Original Tweet, Blue: Retweets, Green: Replies, Orange: Mentions",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(size=10)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        # Simpan visualization
        if output_path:
            fig.write_html(output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/network_{timestamp}.html"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fig.write_html(output_path)
        
        return output_path
    
    def create_influence_chart(self, influential_nodes: List[Dict[str, Any]], output_path: str = None) -> str:
        """Buat chart pengaruh node"""
        if not influential_nodes:
            return ""
        
        # Ambil top 10
        top_nodes = influential_nodes[:10]
        
        labels = [node['label'] for node in top_nodes]
        influence_scores = [node['influence_score'] for node in top_nodes]
        followers = [node['followers'] for node in top_nodes]
        
        # Buat subplot
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Influence Score', 'Followers Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Influence score chart
        fig.add_trace(
            go.Bar(
                x=labels,
                y=influence_scores,
                name='Influence Score',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Followers chart
        fig.add_trace(
            go.Bar(
                x=labels,
                y=followers,
                name='Followers',
                marker_color='lightgreen'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Top Influential Nodes",
            height=500,
            showlegend=False
        )
        
        fig.update_xaxes(tickangle=45)
        
        # Simpan chart
        if output_path:
            fig.write_html(output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/influence_{timestamp}.html"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fig.write_html(output_path)
        
        return output_path
    
    def generate_network_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate laporan analisis jaringan"""
        
        metrics = analysis_result.get('network_metrics', {})
        influential_nodes = analysis_result.get('influential_nodes', [])
        communities = analysis_result.get('communities', {})
        patterns = analysis_result.get('spread_patterns', {})
        
        # Klasifikasi jenis penyebaran
        spread_type = self._classify_spread_type(metrics, patterns)
        
        # Risk assessment
        risk_score = self._calculate_network_risk(metrics, patterns)
        
        # Rekomendasi
        recommendations = self._generate_network_recommendations(spread_type, risk_score)
        
        return {
            'spread_type': spread_type,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'summary': self._generate_network_summary(metrics, patterns),
            'key_findings': self._generate_key_findings(influential_nodes, communities),
            'recommendations': recommendations
        }
    
    def _classify_spread_type(self, metrics: Dict[str, Any], patterns: Dict[str, Any]) -> str:
        """Klasifikasi jenis penyebaran"""
        
        viral_potential = patterns.get('viral_potential', 0)
        echo_chamber = patterns.get('echo_chamber_score', 0)
        bot_influence = patterns.get('bot_influence', 0)
        
        if viral_potential > 0.7:
            return "Viral Spread"
        elif echo_chamber > 0.6:
            return "Echo Chamber"
        elif bot_influence > 0.5:
            return "Bot-Driven"
        elif metrics.get('density', 0) > 0.5:
            return "Concentrated"
        else:
            return "Organic"
    
    def _calculate_network_risk(self, metrics: Dict[str, Any], patterns: Dict[str, Any]) -> float:
        """Hitung skor risiko jaringan"""
        
        risk_factors = [
            patterns.get('viral_potential', 0) * 0.3,
            patterns.get('bot_influence', 0) * 0.4,
            patterns.get('echo_chamber_score', 0) * 0.2,
            min(metrics.get('density', 0), 0.5) * 0.1
        ]
        
        return round(sum(risk_factors), 3)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Dapatkan level risiko"""
        if risk_score > 0.7:
            return "Tinggi"
        elif risk_score > 0.4:
            return "Sedang"
        else:
            return "Rendah"
    
    def _generate_network_summary(self, metrics: Dict[str, Any], patterns: Dict[str, Any]) -> str:
        """Generate ringkasan jaringan"""
        
        num_nodes = metrics.get('num_nodes', 0)
        num_edges = metrics.get('num_edges', 0)
        viral_potential = patterns.get('viral_potential', 0)
        
        return f"Jaringan ini terdiri dari {num_nodes} node dan {num_edges} koneksi. " \
               f"Potensi viral: {viral_potential:.1%}. " \
               f"Tingkat clustering: {patterns.get('echo_chamber_score', 0):.1%}."
    
    def _generate_key_findings(self, influential_nodes: List[Dict[str, Any]], communities: Dict[str, Any]) -> List[str]:
        """Generate temuan kunci"""
        
        findings = []
        
        if influential_nodes:
            top_influencer = influential_nodes[0]
            findings.append(f"Node paling berpengaruh: {top_influencer['label']} (skor: {top_influencer['influence_score']})")
        
        num_communities = communities.get('num_communities', 0)
        if num_communities > 1:
            findings.append(f"Terdeteksi {num_communities} komunitas dalam jaringan")
        
        return findings
    
    def _generate_network_recommendations(self, spread_type: str, risk_score: float) -> List[str]:
        """Generate rekomendasi berdasarkan analisis jaringan"""
        
        recommendations = []
        
        if spread_type == "Viral Spread":
            recommendations.append("Monitor penyebaran dengan cermat")
            recommendations.append("Verifikasi informasi dengan sumber terpercaya")
        
        elif spread_type == "Bot-Driven":
            recommendations.append("Waspadai aktivitas bot dalam penyebaran")
            recommendations.append("Periksa kredibilitas akun yang terlibat")
        
        elif spread_type == "Echo Chamber":
            recommendations.append("Informasi mungkin bias dalam kelompok tertentu")
            recommendations.append("Cari perspektif dari luar komunitas")
        
        if risk_score > 0.5:
            recommendations.append("Tingkat risiko tinggi - perlu investigasi lebih lanjut")
        
        return recommendations 