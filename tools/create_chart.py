from langchain_core.tools import tool
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
import io
from typing import List


@tool
def create_bar_chart(categories: str, values: str, title: str = "Chart", xlabel: str = "X", ylabel: str = "Y") -> str:
    """
    Creates a bar chart and returns it as a base64 encoded PNG string.
    
    Args:
        categories: Comma-separated category labels for x-axis (e.g., "Q1,Q2,Q3,Q4")
        values: Comma-separated numeric values for each category (e.g., "45,62,58,71")
        title: Chart title (default: "Chart")
        xlabel: X-axis label (default: "X")
        ylabel: Y-axis label (default: "Y")
        
    Returns:
        Base64 encoded PNG image string
    """
    try:
        # Parse comma-separated strings into lists
        cat_list = [c.strip() for c in categories.split(',')]
        val_list = [float(v.strip()) for v in values.split(',')]
        
        print(f"\nCreating bar chart with:")
        print(f"  Categories: {cat_list}")
        print(f"  Values: {val_list}")
        print(f"  Title: {title}")
        print(f"  X-label: {xlabel}, Y-label: {ylabel}")
        
        # Create the figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create bar chart
        ax.bar(cat_list, val_list)
        
        # Set labels and title
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        # Encode to base64
        base64_image = base64.b64encode(buffer.read()).decode('utf-8')
        
        plt.close(fig)
        
        print(f"Chart created successfully. Base64 length: {len(base64_image)}")
        return base64_image
        
    except Exception as e:
        return f"Error creating chart: {str(e)}"
