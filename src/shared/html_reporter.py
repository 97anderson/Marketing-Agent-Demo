"""HTML Report Generator for Multi-Agent Workflows.

This module generates beautiful HTML reports from TraceLogger data
using Jinja2 and Tailwind CSS.
"""

import webbrowser
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from src.shared.trace_logger import TraceLogger

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Execution Report - {{ metadata.topic|default('Multi-Agent Workflow') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        dark: {
                            bg: '#0f172a',
                            card: '#1e293b',
                            border: '#334155'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .step-card {
            animation: slideIn 0.3s ease-out;
        }
        .agent-badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- Header -->
        <header class="mb-8">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        🤖 Agent Execution Report
                    </h1>
                    <p class="text-slate-400 mt-2">{{ metadata.topic|default('Multi-Agent Workflow Execution') }}</p>
                </div>
                <div class="text-right text-sm text-slate-400">
                    <div>{{ start_time }}</div>
                    <div class="mt-1">{{ duration|round(2) }}s total</div>
                </div>
            </div>

            <!-- Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <!-- Total Time -->
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div class="text-slate-400 text-sm mb-1">⏱️ Tiempo Total</div>
                    <div class="text-2xl font-bold text-blue-400">{{ duration|round(2) }}s</div>
                </div>

                <!-- Steps -->
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div class="text-slate-400 text-sm mb-1">📊 Total Pasos</div>
                    <div class="text-2xl font-bold text-green-400">{{ total_steps }}</div>
                </div>

                <!-- Success Rate -->
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div class="text-slate-400 text-sm mb-1">✅ Tasa de Éxito</div>
                    <div class="text-2xl font-bold text-purple-400">{{ success_rate|round(1) }}%</div>
                </div>

                <!-- Cost -->
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div class="text-slate-400 text-sm mb-1">💰 Costo Estimado</div>
                    <div class="text-2xl font-bold text-yellow-400">${{ estimated_cost|round(4) }}</div>
                </div>
            </div>

            <!-- Final Result -->
            {% if metadata.final_score %}
            <div class="mt-4 bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <span class="text-slate-400 text-sm">🎯 Resultado Final:</span>
                        <span class="ml-2 text-lg font-bold">
                            {% if metadata.approved %}
                                <span class="text-green-400">✅ APROBADO</span>
                            {% else %}
                                <span class="text-yellow-400">⚠️ APROBADO CON RESERVAS</span>
                            {% endif %}
                        </span>
                    </div>
                    <div class="text-right">
                        <div class="text-sm text-slate-400">Score Final</div>
                        <div class="text-2xl font-bold text-blue-400">{{ metadata.final_score }}/10</div>
                    </div>
                </div>
                {% if metadata.iterations %}
                <div class="mt-2 text-sm text-slate-400">
                    📝 Iteraciones: {{ metadata.iterations }} |
                    🔄 Max Rewrites: {{ metadata.max_rewrites|default(2) }}
                </div>
                {% endif %}
            </div>
            {% endif %}
        </header>

        <!-- Timeline -->
        <div class="space-y-4">
            <h2 class="text-2xl font-bold mb-4 flex items-center">
                <span class="mr-2">📜</span>
                Timeline de Ejecución
            </h2>

            {% for step in steps %}
            <div class="step-card bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-all">
                <div class="flex items-start">
                    <!-- Status Icon -->
                    <div class="mr-4 mt-1">
                        {% if step.status == 'success' %}
                            <div class="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                                <span class="text-green-400 text-lg">✓</span>
                            </div>
                        {% elif step.status == 'failure' %}
                            <div class="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                                <span class="text-red-400 text-lg">✕</span>
                            </div>
                        {% elif step.status == 'tool' %}
                            <div class="w-10 h-10 bg-yellow-500/20 rounded-full flex items-center justify-center">
                                <span class="text-yellow-400 text-lg">🔧</span>
                            </div>
                        {% elif step.status == 'warning' %}
                            <div class="w-10 h-10 bg-orange-500/20 rounded-full flex items-center justify-center">
                                <span class="text-orange-400 text-lg">⚠</span>
                            </div>
                        {% else %}
                            <div class="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
                                <span class="text-blue-400 text-lg">💭</span>
                            </div>
                        {% endif %}
                    </div>

                    <!-- Content -->
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center space-x-2">
                                <!-- Agent Badge -->
                                <span class="agent-badge bg-blue-500/20 text-blue-300 border border-blue-500/30">
                                    {{ step.agent_name }}
                                </span>

                                <!-- Action Type -->
                                <span class="text-sm text-slate-400">{{ step.action_type }}</span>
                            </div>

                            <div class="flex items-center space-x-3 text-sm text-slate-500">
                                {% if step.duration > 0 %}
                                <span>⏱️ {{ step.duration|round(2) }}s</span>
                                {% endif %}
                                <span>{{ step.timestamp }}</span>
                            </div>
                        </div>

                        <!-- Step Content -->
                        <div class="text-slate-300 whitespace-pre-wrap bg-slate-950/50 rounded p-3 border border-slate-800 mt-2">
                            {{ step.content }}
                        </div>

                        <!-- Metadata -->
                        {% if step.metadata %}
                        <div class="mt-3 text-xs text-slate-500">
                            {% for key, value in step.metadata.items() %}
                            <span class="inline-block mr-3">
                                <span class="text-slate-400">{{ key }}:</span> {{ value }}
                            </span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Footer -->
        <footer class="mt-12 text-center text-slate-500 text-sm border-t border-slate-800 pt-6">
            <p>Generated by Marketing Agent v2.0 | Multi-Agent Workflow System</p>
            <p class="mt-1">Report generated at {{ generation_time }}</p>
        </footer>
    </div>
</body>
</html>
"""


class HTMLReporter:
    """Generates HTML reports from TraceLogger data."""

    def __init__(self, trace_logger: TraceLogger):
        """Initialize the HTML reporter.

        Args:
            trace_logger: TraceLogger instance with execution data
        """
        self.trace_logger = trace_logger
        self.template = Template(HTML_TEMPLATE)

    def generate_report(
        self, output_path: str | Path = "agent_execution_report.html", auto_open: bool = True
    ) -> Path:
        """Generate HTML report and save to file.

        Args:
            output_path: Path where to save the HTML report
            auto_open: Whether to automatically open the report in browser

        Returns:
            Path to the generated report
        """
        output_path = Path(output_path)

        # Prepare data for template
        trace_data = self.trace_logger.to_dict()

        # Format steps for display
        formatted_steps = []
        for step_dict in trace_data["steps"]:
            formatted_steps.append(
                {
                    "agent_name": step_dict["agent_name"],
                    "action_type": step_dict["action_type"],
                    "content": step_dict["content"],
                    "status": step_dict["status"],
                    "duration": step_dict["duration"],
                    "timestamp": datetime.fromisoformat(step_dict["timestamp"]).strftime(
                        "%H:%M:%S"
                    ),
                    "metadata": step_dict["metadata"],
                }
            )

        # Render template
        html_content = self.template.render(
            steps=formatted_steps,
            start_time=datetime.fromisoformat(trace_data["start_time"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if trace_data["start_time"]
            else "N/A",
            duration=trace_data["total_duration"],
            total_steps=trace_data["stats"]["total_steps"],
            success_rate=trace_data["stats"]["success_rate"],
            estimated_cost=trace_data["stats"]["estimated_cost"],
            metadata=trace_data["metadata"],
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Save to file
        output_path.write_text(html_content, encoding="utf-8")

        # Auto-open in browser
        if auto_open:
            webbrowser.open(f"file://{output_path.absolute()}")

        return output_path


def generate_report(
    trace_logger: TraceLogger | None = None,
    output_path: str | Path = "agent_execution_report.html",
    auto_open: bool = True,
) -> Path:
    """Convenience function to generate a report.

    Args:
        trace_logger: TraceLogger instance (uses global if None)
        output_path: Path where to save the report
        auto_open: Whether to automatically open in browser

    Returns:
        Path to the generated report
    """
    if trace_logger is None:
        from src.shared.trace_logger import get_trace_logger

        trace_logger = get_trace_logger()

    reporter = HTMLReporter(trace_logger)
    return reporter.generate_report(output_path, auto_open)
