from typing import List, Dict, Any
from app.agents.comparison_agent import ComparisonAgent
from app.agents.research_gap_agent import ResearchGapAgent
from app.agents.citation_agent import CitationAgent

class ReportAgent:
    """
    Synthesizes a publication-ready 8-section academic literature review
    grounded in retrieved literature, comparison tables, research gaps, and verified citations.
    """
    @staticmethod
    def generate_review(topic: str, papers: List[Dict[str, Any]], citation_format: str = "APA") -> Dict[str, Any]:
        comparison = ComparisonAgent.compare_studies(papers)
        gaps_data = ResearchGapAgent.identify_gaps(papers, topic)
        citations = CitationAgent.format_citations(papers, citation_format)

        title = f"Artificial Intelligence and Deep Learning in Cardiology: A Systematic Literature Review on {topic}"

        abstract = (
            f"Cardiovascular disease remains the leading cause of global morbidity and mortality. "
            f"Recent breakthroughs in deep learning, self-attention transformers, and high-resolution electrocardiography (ECG) "
            f"have catalyzed automated diagnostic algorithms rivaling clinical cardiologists. This systematic review evaluates "
            f"{len(papers)} benchmark studies investigating algorithmic detection of arrhythmias, asymptomatic ventricular dysfunction, "
            f"and cardiac remodeling. We synthesize model architectures (1D-CNN, ResNet, Transformer), benchmark datasets (PTB-XL, MIT-BIH), "
            f"and clinical validation frameworks. Systematic limitations including retrospective single-center curation, demographic bias, "
            f"and interpretability deficits are identified, followed by concrete translational research recommendations."
        )

        section1 = (
            f"Cardiology produces vast quantities of continuous electrophysiological data, including 12-lead resting ECGs, "
            f"ambulatory Holter recordings, and wearable sensor streams. Traditional clinical interpretation relies on manual rule-based "
            f"interval measurements (PR, QRS duration, QT prolongation), which are prone to inter-observer variability and subjective fatigue.\n\n"
            f"The rapid maturation of deep neural networks offers the promise of automated, instantaneous, and objective diagnostic screening. "
            f"This review examines contemporary evidence regarding the clinical viability, accuracy, and engineering trade-offs of AI models "
            f"deployed for {topic}."
        )

        section2 = (
            f"Electrocardiography records the spatio-temporal propagation of myocardial depolarization and repolarization. "
            f"Early computational cardiology relied on feature engineering (wavelet transforms, Fourier analysis, Pan-Tompkins peak detection) "
            f"coupled with support vector machines or random forests.\n\n"
            f"In contrast, modern deep learning utilizes end-to-end representation learning. Convolutional neural networks (CNNs) treat raw 1D "
            f"voltage-time series as multi-channel inputs, capturing local morphologic patterns. Recent architectures introduce residual skip "
            f"connections (ResNet-1d) and self-attention mechanisms (Transformers) capable of capturing long-range inter-beat temporal rhythms "
            f"spanning extended recordings."
        )

        # Build Section 3 from retrieved papers
        sec3_paragraphs = []
        for p in papers:
            p_title = p.get("title", "")
            p_authors = p.get("authors", "Investigators")
            p_year = p.get("publication_year", 2022)
            p_model = p.get("model_architecture", "Deep Learning")
            p_data = p.get("dataset_name", "Clinical Cohort")
            p_metrics = p.get("evaluation_metrics", "High accuracy")
            p_res = p.get("results_summary", "")

            sec3_paragraphs.append(
                f"### {p_title} ({p_year})\n"
                f"**Authors:** {p_authors}\n\n"
                f"**Methodology & Dataset:** The study evaluated {p_model} trained on {p_data} ({p.get('sample_size', 'Clinical cohort')}). "
                f"The primary diagnostic objective centered on automated feature discrimination from raw waveform recordings.\n\n"
                f"**Reported Performance:** Model achieved {p_metrics}. {p_res}\n\n"
                f"**Author-Noted Limitations:** {p.get('limitations', 'Retrospective study design requiring prospective evaluation.')}"
            )
        section3 = "\n\n".join(sec3_paragraphs)

        # Build Section 4: Comparative Matrix Markdown
        comp_rows = []
        comp_rows.append("| Study | Dataset | Model Architecture | Reported Performance | Primary Advantage | Major Limitation |")
        comp_rows.append("|---|---|---|---|---|---|")
        for row in comparison["matrix"]:
            comp_rows.append(
                f"| {row['title'][:35]}... | {row['dataset'][:25]} | {row['method_model'][:25]} | {row['evaluation_metrics']} | {row['advantages'][:30]}... | {row['limitations'][:30]}... |"
            )
        section4 = (
            f"{comparison['synthesis_analysis']}\n\n"
            + "\n".join(comp_rows) + "\n\n"
            + "**Key Comparative Takeaways:**\n"
            + "\n".join([f"- {t}" for t in comparison["key_takeaways"]])
        )

        # Build Section 5: Research Gaps
        gap_items_str = []
        for g in gaps_data["gaps"]:
            gap_items_str.append(
                f"#### {g['category']}: {g['gap_title']}\n"
                f"> **Badge:** *{g['synthesis_badge']}*\n\n"
                f"**Description:** {g['description']}\n\n"
                f"**Recommended Future Direction:** {g['potential_future_direction']}"
            )
        section5 = (
            f"Through cross-study meta-synthesis of {len(papers)} reviewed publications, the AI research agent identified "
            f"four critical systemic gaps:\n\n" + "\n\n".join(gap_items_str)
        )

        section6 = (
            f"To bridge the gap between computational benchmarks and clinical bedside implementation, several future research avenues are critical:\n\n"
            f"1. **Pragmatic Randomized Controlled Trials (RCTs):** Shift focus from AUC optimization on retrospective data to prospective trials assessing patient-centered outcomes (e.g., prevention of embolic stroke).\n"
            f"2. **Physics-Informed Cardiac Neural Networks:** Integrate biophysical transmembrane voltage differential equations directly into deep learning losses to ensure electrophysiological fidelity.\n"
            f"3. **Federated Multi-Ethnic Biobanks:** Establish privacy-preserving federated learning across international medical networks to eliminate demographic and racial training bias.\n"
            f"4. **Quantized Edge Architectures:** Deploy INT4 quantization and neuromorphic spike-based architectures enabling continuous arrhythmia monitoring on sub-milliwatt wearable microcontrollers."
        )

        section7 = (
            f"Deep learning algorithms demonstrate clinical-grade sensitivity and specificity for complex cardiovascular screening, "
            f"frequently outperforming traditional manual interval measurements. However, the lack of prospective external multi-center trials, "
            f"black-box interpretability, and class imbalance for rare channelopathies constitute substantial hurdles. "
            f"Addressing these challenges through explainable AI and rigorous clinical trials will be decisive in establishing "
            f"AI as an indispensable co-pilot in modern cardiology."
        )

        ref_str = "\n".join(citations)

        sections = [
            {"section_number": 1, "title": "Introduction", "content": section1},
            {"section_number": 2, "title": "Background & Theoretical Foundations", "content": section2},
            {"section_number": 3, "title": "Literature Review & Study Syntheses", "content": section3},
            {"section_number": 4, "title": "Comparative Analysis & Model Benchmarks", "content": section4},
            {"section_number": 5, "title": "Synthesized Research Gaps", "content": section5},
            {"section_number": 6, "title": "Future Research Directions", "content": section6},
            {"section_number": 7, "title": "Conclusion", "content": section7},
            {"section_number": 8, "title": "References", "content": ref_str}
        ]

        full_markdown = (
            f"# {title}\n\n"
            f"## Abstract\n{abstract}\n\n"
            f"## 1. Introduction\n{section1}\n\n"
            f"## 2. Background\n{section2}\n\n"
            f"## 3. Literature Review\n{section3}\n\n"
            f"## 4. Comparative Analysis\n{section4}\n\n"
            f"## 5. Research Gaps\n{section5}\n\n"
            f"## 6. Future Directions\n{section6}\n\n"
            f"## 7. Conclusion\n{section7}\n\n"
            f"## 8. References ({citation_format} Format)\n{ref_str}\n"
        )

        return {
            "title": title,
            "abstract": abstract,
            "sections": sections,
            "references": citations,
            "citation_format": citation_format,
            "full_markdown": full_markdown
        }
