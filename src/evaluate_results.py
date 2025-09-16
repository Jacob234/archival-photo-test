"""
Evaluation and reporting module for archival photo vision model analysis.

This module provides comprehensive evaluation capabilities for analyzing and reporting
vision model testing results. It generates performance comparisons, cost analyses,
and detailed reports across multiple dimensions (photo type, decade, model performance).

Main functionality:
- Performance metrics analysis across all tested models
- Cost effectiveness comparison and budget planning
- Photo type and decade-based analysis
- Markdown report generation for stakeholder review
- Excel template creation for manual evaluation scoring
- Statistical analysis and recommendations

Example:
    Basic usage to generate all evaluation reports:

    >>> from src.evaluate_results import ResultsEvaluator
    >>> evaluator = ResultsEvaluator()
    >>> evaluator.generate_all_reports()
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

from utils import (
    setup_logging,
    load_json,
    save_json,
    ensure_directory
)

class ResultsEvaluator:
    """
    Comprehensive evaluation and reporting system for vision model testing results.

    This class analyzes test results from multiple vision models and generates
    detailed reports for decision-making. It provides statistical analysis,
    cost comparisons, and performance metrics across different photo categories.

    Key features:
    - Multi-dimensional analysis (model, photo type, decade)
    - Cost-effectiveness calculations
    - Statistical performance metrics
    - Automated report generation in multiple formats
    - Manual evaluation template creation
    - Stakeholder-ready recommendations

    Attributes:
        results_dir: Directory containing test results files
        reports_dir: Directory for saving generated reports
        logger: Configured logger instance
    """

    def __init__(self, results_dir: str = "data/results", reports_dir: str = "reports"):
        """
        Initialize the evaluator.

        Args:
            results_dir: Directory containing test results
            reports_dir: Directory to save evaluation reports
        """
        self.results_dir = results_dir
        self.reports_dir = reports_dir
        self.logger = setup_logging()
        ensure_directory(self.reports_dir)

    def load_results(self) -> Optional[Dict[str, Any]]:
        """
        Load and combine test results and cost analysis data.

        Loads both the main test results and cost analysis files,
        combining them into a unified data structure for analysis.

        Returns:
            Dictionary containing test results and cost analysis, or None if files not found
        """
        results_file = os.path.join(self.results_dir, "model_test_results.json")
        cost_file = os.path.join(self.results_dir, "cost_analysis.json")

        if not os.path.exists(results_file):
            self.logger.error(f"Results file not found: {results_file}")
            return None

        results = load_json(results_file)
        cost_analysis = load_json(cost_file) if os.path.exists(cost_file) else {}

        return {
            "test_results": results,
            "cost_analysis": cost_analysis
        }

    def analyze_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics for all models.

        Analyzes success rates, response quality metrics, processing times,
        and provides statistical summaries across all tested photos.

        Args:
            results: List of test results from all photos and models

        Returns:
            Dictionary with detailed performance analysis including:
            - Success rates and response statistics
            - Average processing times
            - Response length analysis with standard deviation
            - Sample responses for qualitative review
        """
        models = ["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet", "gemini-1.5-flash"]
        analysis = {}

        for model in models:
            model_data = {
                "response_lengths": [],
                "processing_times": [],
                "success_count": 0,
                "total_count": 0,
                "responses": []
            }

            for photo_data in results:
                model_result = photo_data["model_results"].get(model, {})
                model_data["total_count"] += 1

                if model_result.get("success", False):
                    model_data["success_count"] += 1
                    model_data["response_lengths"].append(len(model_result.get("response", "")))
                    model_data["processing_times"].append(model_result.get("processing_time", 0))
                    model_data["responses"].append(model_result.get("response", ""))

            # Calculate metrics
            analysis[model] = {
                "success_rate": model_data["success_count"] / model_data["total_count"] if model_data["total_count"] > 0 else 0,
                "avg_response_length": sum(model_data["response_lengths"]) / len(model_data["response_lengths"]) if model_data["response_lengths"] else 0,
                "avg_processing_time": sum(model_data["processing_times"]) / len(model_data["processing_times"]) if model_data["processing_times"] else 0,
                "response_length_std": pd.Series(model_data["response_lengths"]).std() if model_data["response_lengths"] else 0,
                "successful_responses": len(model_data["responses"]),
                "sample_responses": model_data["responses"][:3]  # Keep 3 sample responses
            }

        return analysis

    def analyze_by_photo_type(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze model performance segmented by photo type categories.

        Breaks down model performance by photo types (portrait, street, building,
        event, work, miscellaneous) to identify strengths and weaknesses of
        each model for specific content types.

        Args:
            results: List of test results from all photos and models

        Returns:
            Dictionary with photo type analysis showing:
            - Success rates by photo type and model
            - Response quality metrics for each category
            - Sample counts for statistical significance
        """
        photo_types = set()
        for photo_data in results:
            photo_types.add(photo_data.get("photo_type", "unknown"))

        analysis = {}
        models = ["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet", "gemini-1.5-flash"]

        for photo_type in photo_types:
            analysis[photo_type] = {}

            for model in models:
                type_results = [
                    photo_data["model_results"].get(model, {})
                    for photo_data in results
                    if photo_data.get("photo_type") == photo_type
                ]

                successful = [r for r in type_results if r.get("success", False)]

                analysis[photo_type][model] = {
                    "total": len(type_results),
                    "successful": len(successful),
                    "success_rate": len(successful) / len(type_results) if type_results else 0,
                    "avg_response_length": sum(len(r.get("response", "")) for r in successful) / len(successful) if successful else 0
                }

        return analysis

    def analyze_by_decade(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze model performance segmented by historical decade.

        Examines how well each model performs on photos from different
        decades (1920s-1980s) to understand temporal bias and accuracy
        across different historical periods.

        Args:
            results: List of test results from all photos and models

        Returns:
            Dictionary with decade analysis showing:
            - Success rates by decade and model
            - Historical accuracy trends
            - Sample distribution across time periods
        """
        decades = set()
        for photo_data in results:
            decades.add(photo_data.get("decade", "unknown"))

        analysis = {}
        models = ["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet", "gemini-1.5-flash"]

        for decade in decades:
            analysis[decade] = {}

            for model in models:
                decade_results = [
                    photo_data["model_results"].get(model, {})
                    for photo_data in results
                    if photo_data.get("decade") == decade
                ]

                successful = [r for r in decade_results if r.get("success", False)]

                analysis[decade][model] = {
                    "total": len(decade_results),
                    "successful": len(successful),
                    "success_rate": len(successful) / len(decade_results) if decade_results else 0,
                    "avg_response_length": sum(len(r.get("response", "")) for r in successful) / len(successful) if successful else 0
                }

        return analysis

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """
        Generate comprehensive stakeholder-ready markdown report.

        Creates a detailed report combining all analysis results into
        a formatted document suitable for decision-makers. Includes
        executive summary, performance comparisons, cost analysis,
        and actionable recommendations.

        Args:
            data: Combined results and analysis data from all evaluation methods

        Returns:
            Formatted markdown report string with:
            - Executive summary with key metrics
            - Performance comparison tables
            - Cost analysis and budget projections
            - Segmented analysis by photo type and decade
            - Implementation recommendations
            - Sample response previews
        """
        report_lines = [
            "# Archival Photo Vision Model Testing Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## Executive Summary\n",
        ]

        # Executive summary
        results = data["test_results"]
        cost_analysis = data["cost_analysis"]
        performance = data["performance_analysis"]

        total_photos = len(results)
        total_models = len(cost_analysis)

        report_lines.extend([
            f"- **Total Photos Tested**: {total_photos}",
            f"- **Models Evaluated**: {total_models}",
            f"- **Test Period**: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Model Performance Summary\n"
        ])

        # Performance table
        perf_data = []
        for model, metrics in performance.items():
            perf_data.append([
                model,
                f"{metrics['success_rate']:.1%}",
                f"{metrics['avg_response_length']:.0f}",
                f"{metrics['avg_processing_time']:.2f}s"
            ])

        perf_table = tabulate(
            perf_data,
            headers=["Model", "Success Rate", "Avg Response Length", "Avg Processing Time"],
            tablefmt="markdown"
        )
        report_lines.append(perf_table + "\n")

        # Cost analysis
        report_lines.append("## Cost Analysis\n")

        cost_data = []
        for model, cost_info in cost_analysis.items():
            cost_data.append([
                model,
                f"${cost_info['total_cost_usd']:.4f}",
                f"${cost_info['avg_cost_per_photo']:.6f}",
                f"${cost_info['cost_per_1000_photos']:.2f}"
            ])

        cost_table = tabulate(
            cost_data,
            headers=["Model", "Total Cost", "Cost per Photo", "Cost per 1000 Photos"],
            tablefmt="markdown"
        )
        report_lines.append(cost_table + "\n")

        # Photo type analysis
        if "photo_type_analysis" in data:
            report_lines.append("## Performance by Photo Type\n")
            type_analysis = data["photo_type_analysis"]

            for photo_type, type_data in type_analysis.items():
                report_lines.append(f"### {photo_type.title()}\n")

                type_perf_data = []
                for model, metrics in type_data.items():
                    type_perf_data.append([
                        model,
                        metrics["total"],
                        f"{metrics['success_rate']:.1%}",
                        f"{metrics['avg_response_length']:.0f}"
                    ])

                type_table = tabulate(
                    type_perf_data,
                    headers=["Model", "Photos", "Success Rate", "Avg Response Length"],
                    tablefmt="markdown"
                )
                report_lines.append(type_table + "\n")

        # Recommendations
        report_lines.extend([
            "## Recommendations\n",
            self._generate_recommendations(data),
            "",
            "## Sample Responses\n"
        ])

        # Add sample responses
        for model, metrics in performance.items():
            if metrics.get("sample_responses"):
                report_lines.append(f"### {model}\n")
                report_lines.append(f"```\n{metrics['sample_responses'][0][:300]}...\n```\n")

        return "\n".join(report_lines)

    def _generate_recommendations(self, data: Dict[str, Any]) -> str:
        """
        Generate actionable recommendations based on comprehensive analysis.

        Analyzes performance and cost data to provide specific recommendations
        for different use cases and budget scenarios.

        Args:
            data: Combined results and analysis data

        Returns:
            Formatted recommendations string with specific guidance for:
            - Best overall performance model selection
            - Most cost-effective options
            - Hybrid implementation strategies
            - Use case-specific model recommendations
        """
        cost_analysis = data["cost_analysis"]
        performance = data["performance_analysis"]

        # Find best performing model
        best_success = max(performance.values(), key=lambda x: x["success_rate"])
        best_model = [k for k, v in performance.items() if v["success_rate"] == best_success["success_rate"]][0]

        # Find most cost-effective model
        cost_effective = min(cost_analysis.values(), key=lambda x: x["avg_cost_per_photo"])
        cost_model = [k for k, v in cost_analysis.items() if v["avg_cost_per_photo"] == cost_effective["avg_cost_per_photo"]][0]

        recommendations = [
            f"**Best Overall Performance**: {best_model} (Success rate: {best_success['success_rate']:.1%})",
            f"**Most Cost-Effective**: {cost_model} (${cost_effective['avg_cost_per_photo']:.6f} per photo)",
            "",
            "**For Library Implementation:**",
            "- For high-quality cataloging: Consider the best performing model",
            "- For budget-conscious operations: Use the most cost-effective model",
            "- For hybrid approach: Use cost-effective model for initial processing, high-quality model for important collections"
        ]

        return "\n".join(recommendations)

    def create_evaluation_spreadsheet(self, data: Dict[str, Any]) -> None:
        """
        Create Excel template for manual qualitative evaluation.

        Generates a structured spreadsheet with model responses and
        empty scoring columns for human evaluators to assess response
        quality across multiple dimensions.

        Args:
            data: Combined results and analysis data

        Outputs:
            Excel file with columns for:
            - Photo metadata and context
            - Model responses
            - Manual scoring fields (accuracy, detail, context, usefulness)
            - Notes section for qualitative feedback
        """
        results = data["test_results"]
        evaluation_data = []

        for photo_data in results:
            base_row = {
                "photo_id": photo_data["photo_id"],
                "wikimedia_title": photo_data["wikimedia_title"],
                "decade": photo_data["decade"],
                "photo_type": photo_data["photo_type"],
                "description": photo_data.get("description", "")[:100]
            }

            # Add model responses
            for model in ["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet", "gemini-1.5-flash"]:
                model_result = photo_data["model_results"].get(model, {})
                response = model_result.get("response", "")

                row = base_row.copy()
                row.update({
                    "model": model,
                    "response": response,
                    "accuracy_score": "",  # For manual scoring
                    "detail_score": "",    # For manual scoring
                    "context_score": "",   # For manual scoring
                    "usefulness_score": "", # For manual scoring
                    "notes": ""            # For manual notes
                })
                evaluation_data.append(row)

        # Save to Excel for easier manual evaluation
        df = pd.DataFrame(evaluation_data)
        excel_file = os.path.join(self.reports_dir, "manual_evaluation_template.xlsx")
        df.to_excel(excel_file, index=False)

        self.logger.info(f"Evaluation spreadsheet created: {excel_file}")

    def generate_all_reports(self) -> None:
        """
        Generate complete suite of evaluation reports and analysis files.

        Orchestrates the full evaluation workflow:
        1. Loads and combines test results
        2. Performs all statistical analyses
        3. Generates markdown report for stakeholders
        4. Creates Excel template for manual evaluation
        5. Saves detailed analysis data for further research

        Outputs:
            - evaluation_report.md: Comprehensive stakeholder report
            - manual_evaluation_template.xlsx: Template for human scoring
            - detailed_analysis.json: Raw analysis data for research
        """
        # Load results
        data = self.load_results()
        if not data:
            return

        # Perform analyses
        data["performance_analysis"] = self.analyze_performance_metrics(data["test_results"])
        data["photo_type_analysis"] = self.analyze_by_photo_type(data["test_results"])
        data["decade_analysis"] = self.analyze_by_decade(data["test_results"])

        # Generate markdown report
        markdown_report = self.generate_markdown_report(data)
        report_file = os.path.join(self.reports_dir, "evaluation_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        # Create evaluation spreadsheet
        self.create_evaluation_spreadsheet(data)

        # Save detailed analysis
        analysis_file = os.path.join(self.reports_dir, "detailed_analysis.json")
        save_json({
            "performance_analysis": data["performance_analysis"],
            "photo_type_analysis": data["photo_type_analysis"],
            "decade_analysis": data["decade_analysis"]
        }, analysis_file)

        self.logger.info(f"All reports generated in {self.reports_dir}")

def main():
    """Main function to generate evaluation reports."""
    evaluator = ResultsEvaluator()
    evaluator.generate_all_reports()

if __name__ == "__main__":
    main()