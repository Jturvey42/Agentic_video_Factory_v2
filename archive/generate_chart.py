import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_roi_chart():
    # Paths adjusted to your E: drive environment
    csv_path = "E:/Agentic_Video_Factory_v2/data/cloud_spend_logs.csv"
    output_path = "E:/Agentic_Video_Factory_v2/assets/roi_output.png"
    
    # Ensure the assets directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Mock data generation if your CSV doesn't exist yet (for instant testing!)
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        mock_data = {
            "Month": list(range(1, 13)),
            "Cumulative_Savings": [-500, -200, 100, 500, 1000, 1600, 2300, 3100, 4000, 5000, 6100, 7300]
        }
        pd.DataFrame(mock_data).to_csv(csv_path, index=False)
        print(f"[Chart] Created mock data log at: {csv_path}")

    # Read the data logs
    df = pd.read_csv(csv_path)
    
    # Apply "The Agentic Engineer" premium dark theme styling
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    # Match the deep slate gray hex codes from your layout engine
    fig.patch.set_facecolor('#14161a')  # Matches right_bg color (20, 22, 26)
    ax.set_facecolor('#14161a')
    
    # Plot the cumulative savings/ROI line
    ax.plot(df['Month'], df['Cumulative_Savings'], color='#00adb5', linewidth=3.5, label='Net Cumulative Savings')
    
    # Draw a stark horizontal line at $0 to visually highlight the "Break-Even" point
    ax.axhline(0, color='#ff5722', linestyle='--', linewidth=1.5, label='Break-Even Line')
    
    # Chart formatting elements
    ax.set_title("Post-Migration Pipeline ROI Trajectory", fontsize=16, pad=20, weight='bold', color='#ffffff')
    ax.set_xlabel("Months Post-Migration", fontsize=12, labelpad=10, color='#aaaaaa')
    ax.set_ylabel("Net Savings / Loss ($)", fontsize=12, labelpad=10, color='#aaaaaa')
    
    # Subtle technical grid lines
    ax.grid(True, linestyle=':', alpha=0.4, color='#444444')
    ax.legend(loc='upper left', facecolor='#1e2024', edgecolor='#444444', fontsize=11)
    
    # Clean up borders for a modern minimalistic look
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#444444')
        
    # Highlight month 4 on the x-axis where it crosses break-even
    ax.set_xticks(df['Month'])
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[Chart] Dynamic chart successfully saved to: {output_path}")

if __name__ == "__main__":
    generate_roi_chart()