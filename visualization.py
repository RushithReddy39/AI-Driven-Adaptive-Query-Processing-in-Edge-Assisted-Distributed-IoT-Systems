import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk  # Import for creating tables
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the metrics_log.csv file
data = pd.read_csv('metrics_log.csv', names=["Device ID", "CPU Load", "RAM Usage", "Bandwidth", "Query Size", "Predicted Route", "Round-Trip Time"])

# Set plot style
sns.set(style="whitegrid")

# Create a Tkinter window
root = tk.Tk()
root.title("Scrollable Visualization of Query Metrics")

# Create a canvas to hold the plots and make it scrollable
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Create a window inside the canvas for the scrollable frame
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.config(yscrollcommand=scrollbar.set)

# Add the canvas and scrollbar to the window
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# 1. Query Response Time Distribution (Histogram + KDE)
fig1 = plt.Figure(figsize=(10, 6))
ax1 = fig1.add_subplot(111)
sns.histplot(data['Round-Trip Time'], kde=True, color='blue', bins=30, ax=ax1)
ax1.set_title('Query Response Time Distribution')
ax1.set_xlabel('Round-Trip Time (seconds)')
ax1.set_ylabel('Frequency')

# Embed the plot in the Tkinter window
canvas1 = FigureCanvasTkAgg(fig1, master=scrollable_frame)
canvas1.draw()
canvas1.get_tk_widget().pack(pady=10)

# 2. Query Response Time vs. CPU Load (Scatter Plot)
fig2 = plt.Figure(figsize=(10, 6))
ax2 = fig2.add_subplot(111)
sns.scatterplot(x=data['CPU Load'], y=data['Round-Trip Time'], hue=data['Predicted Route'], palette="Set1", ax=ax2)
ax2.set_title('Query Response Time vs. CPU Load')
ax2.set_xlabel('CPU Load (%)')
ax2.set_ylabel('Round-Trip Time (seconds)')
ax2.legend(title="Predicted Route")

canvas2 = FigureCanvasTkAgg(fig2, master=scrollable_frame)
canvas2.draw()
canvas2.get_tk_widget().pack(pady=10)

# 3. Query Response Time vs. RAM Usage (Scatter Plot)
fig3 = plt.Figure(figsize=(10, 6))
ax3 = fig3.add_subplot(111)
sns.scatterplot(x=data['RAM Usage'], y=data['Round-Trip Time'], hue=data['Predicted Route'], palette="Set2", ax=ax3)
ax3.set_title('Query Response Time vs. RAM Usage')
ax3.set_xlabel('RAM Usage (GB)')
ax3.set_ylabel('Round-Trip Time (seconds)')
ax3.legend(title="Predicted Route")

canvas3 = FigureCanvasTkAgg(fig3, master=scrollable_frame)
canvas3.draw()
canvas3.get_tk_widget().pack(pady=10)

# 4. Routing Accuracy: Predicted Route Counts (Count Plot)
fig4 = plt.Figure(figsize=(8, 6))
ax4 = fig4.add_subplot(111)
sns.countplot(x='Predicted Route', data=data, palette="Set3", ax=ax4)
ax4.set_title('Routing Accuracy: Predicted Routes')
ax4.set_xlabel('Predicted Route')
ax4.set_ylabel('Count')

canvas4 = FigureCanvasTkAgg(fig4, master=scrollable_frame)
canvas4.draw()
canvas4.get_tk_widget().pack(pady=10)

# 5. CPU Load vs. Predicted Route (Box Plot)
fig5 = plt.Figure(figsize=(10, 6))
ax5 = fig5.add_subplot(111)
sns.boxplot(x='Predicted Route', y='CPU Load', data=data, palette="Set1", ax=ax5)
ax5.set_title('CPU Load Distribution by Predicted Route')
ax5.set_xlabel('Predicted Route')
ax5.set_ylabel('CPU Load (%)')

canvas5 = FigureCanvasTkAgg(fig5, master=scrollable_frame)
canvas5.draw()
canvas5.get_tk_widget().pack(pady=10)

# 6. RAM Usage vs. Predicted Route (Box Plot)
fig6 = plt.Figure(figsize=(10, 6))
ax6 = fig6.add_subplot(111)
sns.boxplot(x='Predicted Route', y='RAM Usage', data=data, palette="Set2", ax=ax6)
ax6.set_title('RAM Usage Distribution by Predicted Route')
ax6.set_xlabel('Predicted Route')
ax6.set_ylabel('RAM Usage (GB)')

canvas6 = FigureCanvasTkAgg(fig6, master=scrollable_frame)
canvas6.draw()
canvas6.get_tk_widget().pack(pady=10)

# **Add Summary Tables and Performance Metrics**
# 7. Create a Table to Show Summary Statistics (e.g., Average Query Response Time, Predicted Route Counts, and Caching Metrics)

# Create a Treeview widget to display summary data in a table format
summary_table = ttk.Treeview(scrollable_frame, columns=("Metric", "Value"), show="headings", height=10)

# Define columns
summary_table.heading("Metric", text="Metric")
summary_table.heading("Value", text="Value")

# Calculate average round-trip time
avg_response_time = data['Round-Trip Time'].mean()

# Calculate routing accuracy (predicted route counts)
route_counts = data['Predicted Route'].value_counts()

# Calculate cache hit rate (for example: queries processed through cache vs total queries)
total_queries = len(data)
cache_hits = len(data[data['Predicted Route'] == "Edge"])  # For simplicity, assume Edge as cache hit
cache_miss = total_queries - cache_hits
cache_hit_rate = cache_hits / total_queries * 100
cache_miss_rate = cache_miss / total_queries * 100

# Insert data into the summary table
summary_table.insert("", "end", values=("Average Query Response Time", round(avg_response_time, 2)))
summary_table.insert("", "end", values=("Device Route Count", route_counts.get('Device', 0)))
summary_table.insert("", "end", values=("Edge Route Count", route_counts.get('Edge', 0)))
summary_table.insert("", "end", values=("Cloud Route Count", route_counts.get('Cloud', 0)))
summary_table.insert("", "end", values=("Cache Hit Rate", f"{round(cache_hit_rate, 2)}%"))
summary_table.insert("", "end", values=("Cache Miss Rate", f"{round(cache_miss_rate, 2)}%"))

# Pack the summary table into the Tkinter window
summary_table.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()
