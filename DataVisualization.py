import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the data
file_path = "company.xlsx"
df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

# Extract numeric values from the Score column
df[['TrustScore', 'Reviews']] = df['Score'].str.extract(r'TrustScore ([\d.]+)\|([\d,]+) reviews')
df['TrustScore'] = pd.to_numeric(df['TrustScore'], errors='coerce')
df['Reviews'] = df['Reviews'].str.replace(',', '').astype(float)

df.fillna({'TrustScore': 0, 'Reviews': 0}, inplace=True)

# GUI Application
class DataVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Company Data Visualizer")
        self.root.geometry("900x700")

        # Title Label
        title_label = tk.Label(root, text="Company Data Visualization", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Button Frame
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Show Trust Scores", command=self.plot_trust_scores).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Show Reviews Distribution", command=self.plot_reviews).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Show Company Locations", command=self.plot_locations).grid(row=0, column=2, padx=10)

        # Canvas for displaying graphs
        self.canvas_frame = ttk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def clear_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def plot_trust_scores(self):
        self.clear_canvas()
        top_companies = df.nlargest(10, 'TrustScore')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_companies['TrustScore'], y=top_companies['Company Name'], hue=top_companies['Company Name'], palette='viridis', legend=False, ax=ax)
        ax.set_xlabel("Trust Score")
        ax.set_ylabel("Company Name")
        ax.set_title("Top 10 Companies by Trust Score")
        self.display_plot(fig)

    def plot_reviews(self):
        self.clear_canvas()
        top_reviews = df.nlargest(10, 'Reviews')
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(top_reviews['Reviews'], labels=top_reviews['Company Name'], autopct='%1.1f%%', colors=sns.color_palette("pastel"))
        ax.set_title("Top 10 Companies by Number of Reviews")
        self.display_plot(fig)

    def plot_locations(self):
        self.clear_canvas()
        
        # Exclude 'Unknown' locations
        location_counts = df[df['Location'] != 'Unknown']['Location'].value_counts().nlargest(10)

        # Check if there is data left to plot
        if location_counts.empty:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        squarify.plot(
            sizes=location_counts.values, 
            label=location_counts.index, 
            alpha=0.7, 
            color=sns.color_palette("magma", len(location_counts)), 
            ax=ax
        )
        
        ax.set_title("Top 10 Locations with Most Companies")
        ax.axis("off")

        self.display_plot(fig)


    def display_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exit_program(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()


# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizerApp(root)
    root.mainloop()
