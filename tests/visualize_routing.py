#!/usr/bin/env python3
"""Visualize routing patterns from test results"""
import json
import os
from datetime import datetime

def create_routing_visualization(results_file: str = None):
    """Create an HTML visualization of routing patterns"""
    
    # Find the latest results file if not specified
    if not results_file:
        files = [f for f in os.listdir('.') if f.startswith('routing_test_results_')]
        if not files:
            print("No routing test results found. Run test_routing.py first.")
            return
        results_file = sorted(files)[-1]
    
    # Load results
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Create HTML visualization
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Bureaucracy Oracle - Routing Patterns</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .metric-label {
            color: #6c757d;
            margin-top: 5px;
        }
        .chart-container {
            margin: 30px 0;
            height: 400px;
        }
        .routing-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }
        .routing-table th, .routing-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .routing-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .correct { color: #28a745; }
        .incorrect { color: #dc3545; }
        .confidence-high { background-color: #d4edda; }
        .confidence-medium { background-color: #fff3cd; }
        .confidence-low { background-color: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ Bureaucracy Oracle - Routing Analysis</h1>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{{ACCURACY}}%</div>
                <div class="metric-label">Routing Accuracy</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{TOTAL}}</div>
                <div class="metric-label">Total Questions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{CORRECT}}</div>
                <div class="metric-label">Correct Routes</div>
            </div>
        </div>
        
        <h2>📊 Agent Selection Distribution</h2>
        <div class="chart-container">
            <canvas id="agentChart"></canvas>
        </div>
        
        <h2>🎯 Routing Accuracy by Expected Agent</h2>
        <div class="chart-container">
            <canvas id="accuracyChart"></canvas>
        </div>
        
        <h2>📋 Routing Details</h2>
        <table class="routing-table">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Question</th>
                    <th>Expected</th>
                    <th>Selected</th>
                    <th>Confidence</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {{TABLE_ROWS}}
            </tbody>
        </table>
    </div>
    
    <script>
        // Agent Distribution Chart
        const agentCtx = document.getElementById('agentChart').getContext('2d');
        new Chart(agentCtx, {
            type: 'doughnut',
            data: {
                labels: {{AGENT_LABELS}},
                datasets: [{
                    data: {{AGENT_DATA}},
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Questions Routed to Each Agent'
                    }
                }
            }
        });
        
        // Accuracy Chart
        const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
        new Chart(accuracyCtx, {
            type: 'bar',
            data: {
                labels: {{ACCURACY_LABELS}},
                datasets: [{
                    label: 'Expected',
                    data: {{EXPECTED_DATA}},
                    backgroundColor: '#36A2EB'
                }, {
                    label: 'Correctly Routed',
                    data: {{CORRECT_DATA}},
                    backgroundColor: '#4BC0C0'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    # Calculate metrics
    summary = data['summary']
    details = data['details']
    
    # Agent distribution
    agent_counts = {}
    for result in details:
        agent = result['selected_agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    # Accuracy by expected agent
    expected_counts = {"bcra": 0, "comex": 0, "senasa": 0}
    correct_counts = {"bcra": 0, "comex": 0, "senasa": 0}
    
    for result in details:
        for agent in result['expected_agents']:
            if agent in expected_counts:
                expected_counts[agent] += 1
                if result['is_correct']:
                    correct_counts[agent] += 1
    
    # Generate table rows
    table_rows = []
    for result in details:
        confidence = result.get('confidence', 0)
        conf_class = 'confidence-high' if confidence > 0.8 else 'confidence-medium' if confidence > 0.6 else 'confidence-low'
        status_class = 'correct' if result['is_correct'] else 'incorrect'
        
        row = f"""
        <tr>
            <td>{result['code']}</td>
            <td>{result['question']}</td>
            <td>{', '.join(result['expected_agents'])}</td>
            <td>{result['selected_agent']}</td>
            <td class="{conf_class}">{confidence:.0%}</td>
            <td class="{status_class}">{result['status']}</td>
        </tr>
        """
        table_rows.append(row)
    
    # Replace placeholders
    html_content = html_content.replace('{{ACCURACY}}', f"{summary['accuracy']*100:.1f}")
    html_content = html_content.replace('{{TOTAL}}', str(summary['total']))
    html_content = html_content.replace('{{CORRECT}}', str(summary['correct']))
    
    html_content = html_content.replace('{{AGENT_LABELS}}', json.dumps(list(agent_counts.keys())))
    html_content = html_content.replace('{{AGENT_DATA}}', json.dumps(list(agent_counts.values())))
    
    html_content = html_content.replace('{{ACCURACY_LABELS}}', json.dumps(['BCRA', 'Comex', 'Senasa']))
    html_content = html_content.replace('{{EXPECTED_DATA}}', json.dumps([expected_counts['bcra'], expected_counts['comex'], expected_counts['senasa']]))
    html_content = html_content.replace('{{CORRECT_DATA}}', json.dumps([correct_counts['bcra'], correct_counts['comex'], correct_counts['senasa']]))
    
    html_content = html_content.replace('{{TABLE_ROWS}}', '\n'.join(table_rows))
    
    # Save HTML file
    output_file = 'routing_visualization.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Visualization created: {output_file}")
    print(f"📊 Open in browser: file://{os.path.abspath(output_file)}")

if __name__ == "__main__":
    create_routing_visualization()