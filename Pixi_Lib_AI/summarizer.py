import os
import google.generativeai as genai
from dotenv import load_dotenv
import fitz

class DocumentSummarizer:
    """
    A class to handle the extraction and summarization of text from
    documents using the Gemini API.
    """

    def __init__(self, api_key: str = None):
        if api_key:
            genai.configure(api_key=api_key) # Corrected line
        else:
            load_dotenv()
            genai.configure(api_key=os.getenv("API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _extract_text(self, file_content: bytes, file_name: str) -> str:
        """
        Extracts text from different file types based on their content.
        """
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == ".pdf":
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                all_text = [page.get_text() for page in doc]
            return "\n".join(all_text)
        elif file_extension == ".txt":
            return file_content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _chunk_text(self, text: str, chunk_size: int = 500000) -> list[str]:
        chunks = []
        current_pos = 0
        while current_pos < len(text):
            end_pos = min(current_pos + chunk_size, len(text))
            chunks.append(text[current_pos:end_pos])
            current_pos = end_pos
        return chunks

    def get_summary(self, full_text: str) -> str:
        """
        Summarizes text using the Gemini API
        """
        if not full_text:
            return "No text provided to summarize."

        # Optimization for texts that don't need chunking
        if len(full_text) < 500000:
            prompt = f"Please provide a detailed summary of the following text:\n{full_text}"
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                return f"Error summarizing text: {e}"

        # Summarize each large chunk (Map-Reduce approach)
        text_chunks = self._chunk_text(full_text)
        chunk_summaries = []
        
        print(f"Text chunked into {len(text_chunks)} parts. Summarizing each part...")

        for i, chunk in enumerate(text_chunks):
            prompt = f"Summarize this portion of a document. This is part {i+1} of {len(text_chunks)}:\n{chunk}"
            try:
                response = self.model.generate_content(prompt)
                chunk_summaries.append(response.text.strip())
                print(f"   -> Summarized chunk {i+1}/{len(text_chunks)}")
            except Exception as e:
                print(f"Error summarizing chunk {i+1}: {e}")
                chunk_summaries.append(f"[Could not summarize chunk {i+1}]")

        print("Consolidating summaries into a final version...")
        
        combined_summaries = "\n".join(chunk_summaries)
        
        final_prompt = f"The following are summaries of sequential parts of a long document. Consolidate them into a single, cohesive, and detailed final summary:\n{combined_summaries}"
        try:
            final_response = self.model.generate_content(final_prompt)
            return final_response.text.strip()
        except Exception as e:
            return f"Error consolidating summaries: {e}"

    def extract_and_summarize_from_path(self, pdf_path: str) -> str:
        """
        A convenience method to extract text from a PDF file path and then summarize it.
        """
        try:
            print(f"Step 1: Extracting text from '{pdf_path}'...")
            with open(pdf_path, "rb") as f:
                file_content = f.read()
            text_from_pdf = self._extract_text(file_content, pdf_path)
            print(f"   -> Successfully extracted {len(text_from_pdf)} characters.\n")
            
            print("Step 2: Generating the summary...")
            final_summary = self.get_summary(text_from_pdf)
            
            return final_summary

        except FileNotFoundError:
            return f"ERROR: The file was not found at '{pdf_path}'. Please check the path and try again."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    # Example usage:
    # NOTE: This part is for demonstration and please remove 
    
    pdf_file_path = "C:\\Users\\Lenovo\\Downloads\\_OceanofPDF.com_God_of_Wrath_-_Rina_Kent.pdf"

    # Initialize the summarizer
    summarizer = DocumentSummarizer()

    # Get the summary from a file path
    final_summary_result = summarizer.extract_and_summarize_from_path(pdf_file_path)
    
    # Print the result
    print("\n--- ✅ FINAL SUMMARY ---")
    print(final_summary_result)

    # Optional: Save the summary to a text file
    if not final_summary_result.startswith("ERROR"):
        with open("summary_output.txt", "w", encoding="utf-8") as f:
            f.write(final_summary_result)
        print("\nSummary saved to summary_output.txt!")