import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


class IrishTransportData:
    def __init__(self):
        """
        Initialize file paths and dataset variables.
        """
        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.BUS_CSV_FILE_PATH = os.path.join(self.PROJECT_ROOT, "data", "BUS_Dataset.csv")
        self.DART_CSV_FILE_PATH = os.path.join(self.PROJECT_ROOT, "data", "DART_Dataset.csv")
        self.LUAS_CSV_FILE_PATH = os.path.join(self.PROJECT_ROOT, "data", "LUAS_Dataset.csv")
        self.encoding = 'latin1'

        self.bus_data = None
        self.dart_data = None
        self.luas_data = None

    def load_data(self):
        """
        Load datasets for Bus, Dart, and Luas.
        """
        try:
            self.bus_data = pd.read_csv(self.BUS_CSV_FILE_PATH, encoding=self.encoding)
            self.dart_data = pd.read_csv(self.DART_CSV_FILE_PATH, encoding=self.encoding)
            self.luas_data = pd.read_csv(self.LUAS_CSV_FILE_PATH, encoding=self.encoding)
            print("Datasets loaded successfully.")
        except Exception as e:
            print(f"Error loading datasets: {e}")

    def check_missing_values(self):
        """
        Check for missing values in the datasets.
        """
        if self.bus_data is not None and self.dart_data is not None and self.luas_data is not None:
            bus_missing = self.bus_data.isnull().sum()
            dart_missing = self.dart_data.isnull().sum()
            luas_missing = self.luas_data.isnull().sum()
            return bus_missing, dart_missing, luas_missing
        else:
            print("Datasets are not loaded. Use the load_data() method first.")
            return None, None, None

    def handle_missing_values(self):
        """
        Handle missing values in the DART dataset.
        """
        if self.dart_data is not None:
            fill_columns = [
                'ATM', 'Weekend Working', 'Wi-Fi & Internet Access',
                'Refreshments', 'Phone Charging', 'Ticket Vending Machine', 'Smart Card Enabled'
            ]
            for column in fill_columns:
                self.dart_data[column] = self.dart_data[column].fillna('Unknown')

            self.dart_data['Eircode'] = self.dart_data['Eircode'].fillna('Unknown')
            self.dart_data['Station Address'] = self.dart_data['Station Address'].fillna('Address Missing')

            print("Missing values handled successfully.")
        else:
            print("DART dataset is not loaded. Use the load_data() method first.")

    def clean_data(self):
        """
        Clean text fields in datasets for uniformity.
        """
        if self.bus_data is not None and self.dart_data is not None and self.luas_data is not None:
            datasets = [self.bus_data, self.dart_data, self.luas_data]
            for dataset in datasets:
                for col in dataset.select_dtypes(include=['object']).columns:
                    dataset[col] = dataset[col].str.strip().str.lower()
            print("Data cleaning completed.")
        else:
            print("One or more datasets are not loaded. Use the load_data() method first.")

    def exploratory_data_analysis(self, data):
        """
        Perform basic exploratory data analysis (EDA) on a dataset.
        """
        if data is not None:
            print("Basic Statistics:")
            print(data.describe(include='all'))
            print("\nUnique Values per Column:")
            print(data.nunique())
            print("\nSample Data:")
            print(data.head())
        else:
            print("Dataset not loaded.")

    def plot_weekend_operational(self, data):
        """
        Plot graph for stations operational on weekends.
        """
        if "Weekend Working" in data.columns:
            counts = data["Weekend Working"].value_counts()
            fig, ax = plt.subplots(figsize=(8, 6))
            counts.plot(kind="bar", color="skyblue", ax=ax)
            ax.set_title("Number of Stations Operational on Weekends")
            ax.set_xlabel("Weekend Status")
            ax.set_ylabel("Number of Stations")
            plt.xticks(rotation=0)
            return fig
        else:
            print("'Weekend Working' column not found in the dataset.")

    def plot_station_facilities(self, data):
        """
        Plot graph for stations with specific facilities.
        """
        facility_columns = [
            "ATM", "Wi-Fi & Internet Access", "Refreshments",
            "Phone Charging", "Ticket Vending Machine", "Smart Card Enabled"
        ]
        facility_counts = {}
        for facility in facility_columns:
            if facility in data.columns:
                facility_counts[facility] = data[facility].value_counts().get('yes', 0)

        fig, ax = plt.subplots(figsize=(11, 7))
        ax.bar(facility_counts.keys(), facility_counts.values(), color="coral")
        ax.set_title("Number of Stations with Specific Facilities")
        ax.set_xlabel("Facilities")
        ax.set_ylabel("Number of Stations")
        plt.xticks(rotation=45, ha='right')
        return fig

    def plot_common_stations_in_routes(self, data, top_n=10):
        """
        Plot graph for most common stations in routes serviced.
        """
        if "Routes Serviced" in data.columns:
            all_routes = data["Routes Serviced"].str.split(",").explode()
            station_counts = all_routes.value_counts()

            fig, ax = plt.subplots(figsize=(12, 6))
            station_counts.head(top_n).plot(kind="bar", color="lightgreen", ax=ax)
            ax.set_title(f"Top {top_n} Most Common Stations in Routes Serviced")
            ax.set_xlabel("Station Name")
            ax.set_ylabel("Frequency in Routes")
            plt.xticks(rotation=45, ha='right')
            return fig
        else:
            print("'Routes Serviced' column not found in the dataset.")

    def advanced_correlation_analysis(self, data):
        """
        Perform correlation analysis between numeric columns.
        """
        if data is not None:
            numeric_data = data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                correlation_matrix = numeric_data.corr()
                print("Correlation Matrix:")
                print(correlation_matrix)

                # Heatmap visualization
                fig, ax = plt.subplots(figsize=(10, 8))
                cax = ax.matshow(correlation_matrix, cmap='coolwarm')
                plt.colorbar(cax)
                ax.set_xticks(range(len(correlation_matrix.columns)))
                ax.set_xticklabels(correlation_matrix.columns, rotation=90)
                ax.set_yticks(range(len(correlation_matrix.columns)))
                ax.set_yticklabels(correlation_matrix.columns)
                ax.set_title("Correlation Heatmap", pad=20)
                return fig
            else:
                print("No numeric columns found for correlation analysis.")
        else:
            print("Dataset not loaded.")