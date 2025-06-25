import streamlit as st
import pandas as pd
import uuid

# Page configuration
st.set_page_config(
    page_title="Interactive Text Annotation Tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .text-passage {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 20px;
    }
    
    .annotation-section {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    .section-header {
        color: #1f77b4;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .stDataEditor {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state with default data if not exists"""
    
    if 'text_passages' not in st.session_state:
        st.session_state.text_passages = [
            "Dies ist der erste Beispielabsatz. Er enthält grundlegende Informationen.",
            "Dieser zweite Absatz bietet ergänzende Details und Kontext zum Thema."
        ]
    
    if 'annotations' not in st.session_state:
        # Initialize annotations for each passage
        st.session_state.annotations = {
            0: pd.DataFrame({
                'Citation': [
                    'Beispielabsatz',
                    'grundlegende Informationen.'
                ],
                'Metadata': [
                    'Author: Mustermann, Year: 2023, Page: 45',
                    'Author: Schmidt, Year: 2022, Chapter: 3'
                ],
                'Annotation_Text': [
                    'Diese Passage führt in das Thema ein und stellt die Grundlagen dar.',
                    'Der Begriff "grundlegende Informationen" bezieht sich auf Basisdaten.'
                ]
            }),
            1: pd.DataFrame({
                'Citation': [
                    'Weber, K. (2024). Kontextuelle Analyse. Band 2, S. 78.'
                ],
                'Metadata': [
                    'Author: Weber, Year: 2024, Volume: 2, Page: 78'
                ],
                'Annotation_Text': [
                    'Dieser Absatz erweitert die Grundlagen um wichtige Kontextinformationen.'
                ]
            })
        }

def add_annotation_row(passage_index):
    """Add a new empty row to the annotations for a specific passage"""
    new_row = pd.DataFrame({
        'Citation': [''],
        'Metadata': [''],
        'Annotation_Text': ['']
    })
    st.session_state.annotations[passage_index] = pd.concat(
        [st.session_state.annotations[passage_index], new_row], 
        ignore_index=True
    )

def remove_annotation_row(passage_index, row_index):
    """Remove a specific row from annotations"""
    if len(st.session_state.annotations[passage_index]) > row_index:
        st.session_state.annotations[passage_index] = st.session_state.annotations[passage_index].drop(
            index=row_index
        ).reset_index(drop=True)

def add_text_passage():
    """Add a new text passage"""
    st.session_state.text_passages.append("Neuer Textabsatz...")
    new_index = len(st.session_state.text_passages) - 1
    st.session_state.annotations[new_index] = pd.DataFrame({
        'Citation': [''],
        'Metadata': [''],
        'Annotation_Text': ['']
    })

def remove_text_passage(index):
    """Remove a text passage and its annotations"""
    if len(st.session_state.text_passages) > 1:
        st.session_state.text_passages.pop(index)
        # Remove annotations for this passage
        if index in st.session_state.annotations:
            del st.session_state.annotations[index]
        # Reindex remaining annotations
        new_annotations = {}
        for i, passage in enumerate(st.session_state.text_passages):
            old_index = i if i < index else i + 1
            if old_index in st.session_state.annotations:
                new_annotations[i] = st.session_state.annotations[old_index]
            else:
                new_annotations[i] = pd.DataFrame({
                    'Citation': [''],
                    'Metadata': [''],
                    'Annotation_Text': ['']
                })
        st.session_state.annotations = new_annotations

def export_data():
    """Export all data as a structured dictionary"""
    export_data = {
        'text_passages': st.session_state.text_passages,
        'annotations': {}
    }
    
    for passage_index, annotations_df in st.session_state.annotations.items():
        export_data['annotations'][passage_index] = annotations_df.to_dict('records')
    
    return export_data

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Application header
    st.title("📝 Interactive Text Annotation Tool")
    st.markdown("---")
    
    # Control buttons in sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        
        if st.button("➕ Add Text Passage", use_container_width=True):
            add_text_passage()
            st.rerun()
        
        st.markdown("### 📊 Export Data")
        if st.button("📥 Show Export Data", use_container_width=True):
            st.json(export_data())
        
        st.markdown("### ℹ️ Instructions")
        st.markdown("""
        **How to use:**
        1. Edit text passages directly in the text areas
        2. Modify annotations in the tables
        3. Use ➕/➖ buttons to add/remove annotations
        4. Add new text passages with the sidebar button
        """)
    
    # Main content area
    for passage_index, passage_text in enumerate(st.session_state.text_passages):
        
        # Create columns for text and annotations
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Text passage section
            # --- NEU: Text Passage mit Markierung anzeigen ---
            # Hole alle Citation-Werte für diese Passage
            citations = []
            if passage_index in st.session_state.annotations:
                citations = [
                    c for c in st.session_state.annotations[passage_index].get('Citation', []) if c
                ]
            # Markiere alle Citation-Vorkommen im Text
            def highlight_citations(text, citations):
                highlighted = text
                # Sortiere nach Länge, damit längere zuerst ersetzt werden
                for citation in sorted(citations, key=len, reverse=True):
                    if citation and citation in highlighted:
                        highlighted = highlighted.replace(
                            citation,
                            f'<mark style="background-color: #b9f6ca">{citation}</mark>'
                        )
                return highlighted

            highlighted_text_passage = highlight_citations(passage_text, citations)
            st.markdown(
                f'<div class="section-header">📄 Text Passage {passage_index + 1}</div>'
                f'<div class="text-passage">{highlighted_text_passage}</div>',
                unsafe_allow_html=True
            )
            # --- ENDE NEU ---

            # Editable text area
            new_text = st.text_area(
                f"Edit Text Passage {passage_index + 1}",
                value=passage_text,
                height=68,
                key=f"text_passage_{passage_index}",
                label_visibility="collapsed"
            )
            
            # Update text in session state
            st.session_state.text_passages[passage_index] = new_text

            # Passage mit Markierungen anzeigen (wie bisher)
            highlighted_text = highlight_citations(new_text, citations)
            st.markdown(
                f'<div style="margin-top:10px; margin-bottom:10px; background:#f9fbe7; padding:10px; border-radius:6px;">'
                f'<b>Passage mit Markierung:</b><br>{highlighted_text}</div>',
                unsafe_allow_html=True
            )

            # Remove passage button (only if more than one passage exists)
            if len(st.session_state.text_passages) > 1:
                if st.button(f"🗑️ Remove Passage {passage_index + 1}", 
                           key=f"remove_passage_{passage_index}"):
                    remove_text_passage(passage_index)
                    st.rerun()
        
        with col2:
            # Annotations section
            st.markdown(f'<div class="section-header">📋 Annotations for Passage {passage_index + 1}</div>', 
                       unsafe_allow_html=True)
            
            # Ensure annotations exist for this passage
            if passage_index not in st.session_state.annotations:
                st.session_state.annotations[passage_index] = pd.DataFrame({
                    'Citation': [''],
                    'Metadata': [''],
                    'Annotation_Text': ['']
                })
            
            # Editable annotations table
            edited_annotations = st.data_editor(
                st.session_state.annotations[passage_index],
                use_container_width=True,
                num_rows="dynamic",
                key=f"annotations_{passage_index}",
                column_config={
                    "Citation": st.column_config.TextColumn(
                        "Citation",
                        help="Source citation for verification",
                        width="medium"
                    ),
                    "Metadata": st.column_config.TextColumn(
                        "Metadata",
                        help="Source metadata (author, year, etc.)",
                        width="medium"
                    ),
                    "Annotation_Text": st.column_config.TextColumn(
                        "Annotation Text",
                        help="Explanations and comments",
                        width="large"
                    )
                }
            )
            
            # Update annotations in session state
            st.session_state.annotations[passage_index] = edited_annotations
            
            # Annotation control buttons
            col_add, col_info = st.columns([1, 1])
            
            with col_add:
                if st.button(f"➕ Add Annotation", 
                           key=f"add_annotation_{passage_index}"):
                    add_annotation_row(passage_index)
                    st.rerun()
            
            with col_info:
                st.caption(f"📊 {len(edited_annotations)} annotation(s)")
        
        # Visual separator between passages
        if passage_index < len(st.session_state.text_passages) - 1:
            st.markdown("---")
    
    # Footer with statistics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Text Passages", len(st.session_state.text_passages))
    
    with col2:
        total_annotations = sum(len(df) for df in st.session_state.annotations.values())
        st.metric("📋 Total Annotations", total_annotations)
    
    with col3:
        total_words = sum(len(text.split()) for text in st.session_state.text_passages)
        st.metric("📝 Total Words", total_words)

if __name__ == "__main__":
    main()
