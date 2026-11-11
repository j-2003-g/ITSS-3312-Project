
# Week 10: Dallas Homicide Clearance Trend
# This program reads our Week 9 results and creates a line chart.

import pandas as pd                  # Used to read and organize CSV data
import matplotlib.pyplot as plt       # Used to create charts

def main():
    # STEP 1: Read the CSV file created in Week 9
    s = pd.read_csv("reports/dallas_series.csv")

    # STEP 2: Convert clearance rates into percentages
    # Example: 0.80 becomes 80%
    s["pct"] = s["clearance"] * 100

    # STEP 3: Make sure all years from 1965 to 2025 are represented
    # set_index("year") makes the year the row label
    # reindex() inserts missing years with NaN values
    # Matplotlib will leave gaps wherever there is a NaN
    full = s.set_index("year").reindex(range(1965, 2026))

    # STEP 4: Create the chart
    # fig = the whole picture
    # ax = the area where the data is plotted
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw the clearance-rate line
    # full.index contains the years
    # full["pct"] contains the percentages
    ax.plot(full.index, full["pct"], marker="o", linewidth=1.5)

    # STEP 5: Set the axis limits, labels, and title
    ax.set_ylim(0, 100)  # Y-axis starts at 0 and ends at 100

    ax.set_xlabel("Year")  # Label the horizontal axis

    # Include the source as required by the professor
    ax.set_ylabel(
        "Homicide clearance (%)\n"
        "Source: FBI UCR via Murder Accountability Project"
    )

    # Explain what, where, and when the chart represents
    ax.set_title(
        "Dallas Police Department Homicide Clearance Rate, 1965–2025"
    )

    # Add light gridlines to make the chart easier to read
    ax.grid(alpha=0.3)

    # STEP 6: Annotate our suspicious year, 2018
    # Week 9 identified 2018 as the largest year-over-year drop
    yr = 2018

    # Find the percentage for 2018
    # loc filters the rows to year 2018
    # iloc[0] selects the first matching value
    val = float(s.loc[s["year"] == yr, "pct"].iloc[0])

    # Add an arrow and explanation pointing to 2018
    ax.annotate(
        f"{yr}: {val:.0f}% — sharp drop",
        xy=(yr, val),             # Point the arrow at 2018
        xytext=(1990, 25),       # Position the explanation
        arrowprops=dict(arrowstyle="->")
    )

    # STEP 7: Mark 2025 as a partial reporting year
    # This prevents readers from treating it as a final result
    ax.annotate(
        "2025: partial year",
        xy=(2025, float(s.loc[s["year"] == 2025, "pct"].iloc[0])),
        xytext=(2005, 15),
        arrowprops=dict(arrowstyle="->")
    )

    # STEP 8: Save the chart as a PNG file
    fig.tight_layout()  # Adjust spacing so labels fit
    fig.savefig("reports/clearance_trend.png", dpi=150)

    # Close the chart to free memory
    plt.close(fig)

    print("Chart saved to reports/clearance_trend.png")


# Run main() only when this file is executed as a program
if __name__ == "__main__":
    main()
