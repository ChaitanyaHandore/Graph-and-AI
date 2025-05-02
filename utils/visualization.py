import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import networkx as nx
from pyvis.network import Network

class TransportVisualization:
    def __init__(self, bus_data, dart_data, luas_data):
        self.bus_data = bus_data
        self.dart_data = dart_data
        self.luas_data = luas_data

    # --------------------------------------
    # Visualizations for BUS_Dataset
    # --------------------------------------
    def plot_frequency_vs_duration(self):
        """
        Scatter plot: Frequency vs. Duration
        Dataset: BUS_Dataset
        """
        if "Frequency" in self.bus_data.columns and "Duration" in self.bus_data.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.bus_data.plot.scatter(x="Frequency", y="Duration", color="blue", alpha=0.6, ax=ax)
            ax.set_title("Frequency vs. Duration", fontsize=14)
            ax.set_xlabel("Frequency", fontsize=12)
            ax.set_ylabel("Duration (mins)", fontsize=12)
            st.pyplot(fig)
        else:
            st.error("Columns 'Frequency' or 'Duration' not found in BUS dataset.")

    def plot_top_routes_by_landmarks(self):
        """
        Bar chart: Top Routes by Key Landmarks
        Dataset: BUS_Dataset
        """
        if "Route Number" in self.bus_data.columns and "Key Landmarks" in self.bus_data.columns:
            landmarks_count = self.bus_data["Key Landmarks"].str.split(",").apply(len)
            self.bus_data["Landmarks Count"] = landmarks_count
            top_routes = self.bus_data.sort_values("Landmarks Count", ascending=False)

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_routes["Route Number"].head(10), top_routes["Landmarks Count"].head(10), color="orange")
            ax.set_title("Top 10 Routes by Key Landmarks", fontsize=14)
            ax.set_xlabel("Route Number", fontsize=12)
            ax.set_ylabel("Number of Key Landmarks", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Columns 'Route Number' or 'Key Landmarks' not found in BUS dataset.")

    def plot_heatmap_landmarks(self):
        """
        Heatmap: Routes vs Number of Key Landmarks
        Dataset: BUS_Dataset
        """
        if "Route Number" in self.bus_data.columns and "Key Landmarks" in self.bus_data.columns:
            self.bus_data["Landmarks Count"] = self.bus_data["Key Landmarks"].str.split(",").apply(len)
            pivot_table = self.bus_data.pivot_table(
                index="Route Number", values="Landmarks Count", aggfunc="sum"
            )
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(pivot_table, annot=True, fmt="g", cmap="coolwarm", ax=ax)
            ax.set_title("Heatmap of Key Landmarks by Routes", fontsize=14)
            st.pyplot(fig)
        else:
            st.error("Columns 'Route Number' or 'Key Landmarks' not found in BUS dataset.")
    # --------------------------------------
    # Visualizations for DART_Dataset
    # --------------------------------------
    def plot_facilities_availability(self):
        """
        Bar chart: Facilities Availability
        Dataset: DART_Dataset
        """
        facility_columns = [
            "ATM", "Wi-Fi & Internet Access", "Refreshments",
            "Phone Charging", "Ticket Vending Machine", "Smart Card Enabled"
        ]
        facilities_count = {col: self.dart_data[col].value_counts().get("Yes", 0) for col in facility_columns}

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(facilities_count.keys(), facilities_count.values(), color="green")
        ax.set_title("Facilities Availability in DART Stations", fontsize=14)
        ax.set_xlabel("Facilities", fontsize=12)
        ax.set_ylabel("Number of Stations", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    def plot_weekend_operational_stations(self):
        """
        Pie chart: Weekend Working Stations
        Dataset: DART_Dataset
        """
        if "Weekend Working" in self.dart_data.columns:
            weekend_counts = self.dart_data["Weekend Working"].value_counts()
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(weekend_counts, labels=weekend_counts.index, autopct='%1.1f%%', colors=["skyblue", "coral"])
            ax.set_title("Weekend Working Stations", fontsize=14)
            st.pyplot(fig)
        else:
            st.error("Column 'Weekend Working' not found in DART dataset.")

    def plot_routes_serviced_per_station(self):
        """
        Bar chart: Routes Serviced Per Station
        Dataset: DART_Dataset
        """
        if "Routes Serviced" in self.dart_data.columns:
            routes_count = self.dart_data["Routes Serviced"].str.split(",").apply(len)
            self.dart_data["Routes Count"] = routes_count
            top_stations = self.dart_data.sort_values("Routes Count", ascending=False)

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_stations["StationName"].head(10), top_stations["Routes Count"].head(10), color="purple")
            ax.set_title("Top 10 Stations by Routes Serviced", fontsize=14)
            ax.set_xlabel("Station Name", fontsize=12)
            ax.set_ylabel("Number of Routes", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Column 'Routes Serviced' not found in DART dataset.")

    def plot_treemap_facilities(self):
        """
        Treemap: Facilities Distribution
        Dataset: DART_Dataset
        """
        facility_columns = [
            "ATM", "Wi-Fi & Internet Access", "Refreshments",
            "Phone Charging", "Ticket Vending Machine", "Smart Card Enabled"
        ]

        facilities_count = {
            col: self.dart_data[col].value_counts().get("Yes", 0) for col in facility_columns
        }
        if facilities_count:
            import plotly.express as px
            treemap_data = pd.DataFrame(list(facilities_count.items()), columns=["Facility", "Count"])
            fig = px.treemap(treemap_data, path=["Facility"], values="Count", title="Facility Distribution")
            st.plotly_chart(fig)
        else:
            st.error("Facility data not found in DART dataset.")
    # --------------------------------------
    # Visualizations for LUAS_Dataset
    # --------------------------------------
    def plot_footfall_by_line(self):
        """
        Bar chart: Footfall by Line
        Dataset: LUAS_Dataset
        """
        if "Line" in self.luas_data.columns and "Daily Footfall" in self.luas_data.columns:
            self.luas_data["Daily Footfall"] = self.luas_data["Daily Footfall"].str.replace(",", "").astype(float)
            footfall = self.luas_data.groupby("Line")["Daily Footfall"].sum()

            fig, ax = plt.subplots(figsize=(10, 6))
            footfall.plot(kind="bar", color="gold", ax=ax)
            ax.set_title("Footfall by Line", fontsize=14)
            ax.set_xlabel("Line", fontsize=12)
            ax.set_ylabel("Total Daily Footfall", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Columns 'Line' or 'Daily Footfall' not found in LUAS dataset.")

    def plot_footfall_trends(self):
        """
        Line Chart: Daily Footfall Trends by Line
        Dataset: LUAS_Dataset
        """
        if "Line" in self.luas_data.columns and "Daily Footfall" in self.luas_data.columns:
            self.luas_data["Daily Footfall"] = self.luas_data["Daily Footfall"].str.replace(",", "").astype(float)
            footfall_trends = self.luas_data.groupby("Line")["Daily Footfall"].sum()

            fig, ax = plt.subplots(figsize=(12, 6))
            footfall_trends.plot(kind="line", marker="o", ax=ax)
            ax.set_title("Daily Footfall Trends by Line", fontsize=14)
            ax.set_xlabel("Line", fontsize=12)
            ax.set_ylabel("Total Daily Footfall", fontsize=12)
            st.pyplot(fig)
        else:
            st.error("Columns 'Line' or 'Daily Footfall' not found in LUAS dataset.")

    def plot_parking_availability(self):
        """
        Count of stations offering parking
        Dataset: LUAS_Dataset
        """
        if "Parking Availability" in self.luas_data.columns:
            parking_counts = self.luas_data["Parking Availability"].value_counts()

            fig, ax = plt.subplots(figsize=(8, 6))
            parking_counts.plot(kind="bar", color="brown", ax=ax)
            ax.set_title("Parking Availability at LUAS Stations", fontsize=14)
            ax.set_xlabel("Parking Availability", fontsize=12)
            ax.set_ylabel("Number of Stations", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Column 'Parking Availability' not found in LUAS dataset.")

    def plot_accessibility_comparison(self):
        """
        Bar chart: Accessible vs Non-accessible stations
        Dataset: LUAS_Dataset
        """
        if "Accessibility" in self.luas_data.columns:
            accessibility_counts = self.luas_data["Accessibility"].value_counts()

            fig, ax = plt.subplots(figsize=(8, 6))
            accessibility_counts.plot(kind="bar", color="teal", ax=ax)
            ax.set_title("Accessibility Comparison", fontsize=14)
            ax.set_xlabel("Accessibility", fontsize=12)
            ax.set_ylabel("Number of Stations", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Column 'Accessibility' not found in LUAS dataset.")

    def plot_nearby_landmarks(self):
        """
        Count of stations with nearby landmarks
        Dataset: LUAS_Dataset
        """
        if "Nearby Landmarks" in self.luas_data.columns:
            landmarks_count = self.luas_data["Nearby Landmarks"].str.split(",").apply(len)

            fig, ax = plt.subplots(figsize=(10, 6))
            landmarks_count.plot(kind="bar", color="magenta", ax=ax)
            ax.set_title("Nearby Landmarks at LUAS Stations", fontsize=14)
            ax.set_xlabel("Station Index", fontsize=12)
            ax.set_ylabel("Number of Nearby Landmarks", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.error("Column 'Nearby Landmarks' not found in LUAS dataset.")

    def plot_station_zone_relationship(self):
        """
        Bar chart: LUAS Station Name grouped by Zone
        Dataset: LUAS_Dataset
        """
        if "Station Name" in self.luas_data.columns and "Zone" in self.luas_data.columns:
            # Group data by Zone
            zone_station_counts = self.luas_data.groupby("Zone")["Station Name"].count().sort_values(ascending=False)

            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 6))
            zone_station_counts.plot(kind="bar", color="purple", ax=ax)
            ax.set_title("Number of Stations per Zone", fontsize=14)
            ax.set_xlabel("Zone", fontsize=12)
            ax.set_ylabel("Number of Stations", fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Display data as a table for reference
            st.subheader("Station Count per Zone")
            st.dataframe(zone_station_counts.reset_index().rename(columns={"Station Name": "Station Count"}))
        else:
            st.error("Columns 'Station Name' or 'Zone' not found in LUAS dataset.")

    def plot_accessibility_sunburst(self):
        """
        Sunburst Chart: Accessibility by Zone
        Dataset: LUAS_Dataset
        """
        if "Accessibility" in self.luas_data.columns and "Zone" in self.luas_data.columns:
            import plotly.express as px
            fig = px.sunburst(
                self.luas_data,
                path=["Zone", "Accessibility"],
                title="Accessibility Distribution by Zone",
                color="Zone",
            )
            st.plotly_chart(fig)
        else:
            st.error("Columns 'Accessibility' or 'Zone' not found in LUAS dataset.")

    # --------------------------------------
    # Visualizations for LUAS_Dataset
    # --------------------------------------