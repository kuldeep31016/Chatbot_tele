import pandas as pd
import streamlit as st
import os

class DataLoader:
    def __init__(self):
        self.medicine_data = None
        self.precaution_data = None
        self.adherence_data = None
        self.side_effects_data = None
        self.load_all_data()
    
    def load_all_data(self):
        """Load all CSV datasets"""
        try:
            # Load medicine details
            self.medicine_data = pd.read_csv('attached_assets/Medicine_Details_1757614301051.csv')
            
            # Load disease precautions
            self.precaution_data = pd.read_csv('attached_assets/Disease precaution_1757614301052.csv')
            
            # Load patient adherence data
            self.adherence_data = pd.read_csv('attached_assets/patient_adherence_dataset_1757614301052.csv')
            
            # Load drug side effects
            self.side_effects_data = pd.read_csv('attached_assets/drugs_side_effects_drugs_com_1757614310610.csv')
            
            # Clean the data
            self._clean_data()
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def _clean_data(self):
        """Clean and preprocess the loaded data"""
        if self.medicine_data is not None:
            # Clean medicine data
            self.medicine_data = self.medicine_data.dropna(subset=['Medicine Name'])
            self.medicine_data['Medicine Name'] = self.medicine_data['Medicine Name'].str.strip()
            
            # Convert review percentages to numeric
            for col in ['Excellent Review %', 'Average Review %', 'Poor Review %']:
                if col in self.medicine_data.columns:
                    self.medicine_data[col] = self.medicine_data[col].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        if self.precaution_data is not None:
            # Clean precaution data
            self.precaution_data = self.precaution_data.dropna(subset=['Disease'])
            self.precaution_data['Disease'] = self.precaution_data['Disease'].str.strip()
        
        if self.adherence_data is not None:
            # Clean adherence data
            self.adherence_data = self.adherence_data.dropna()
        
        if self.side_effects_data is not None:
            # Clean side effects data
            self.side_effects_data = self.side_effects_data.dropna(subset=['drug_name'])
            self.side_effects_data['drug_name'] = self.side_effects_data['drug_name'].str.strip()
    
    def get_medicine_data(self):
        """Get medicine details data"""
        return self.medicine_data
    
    def get_precaution_data(self):
        """Get disease precautions data"""
        return self.precaution_data
    
    def get_adherence_data(self):
        """Get patient adherence data"""
        return self.adherence_data
    
    def get_side_effects_data(self):
        """Get drug side effects data"""
        return self.side_effects_data
    
    def get_diseases_list(self):
        """Get list of all diseases from precaution data"""
        if self.precaution_data is not None:
            return self.precaution_data['Disease'].unique().tolist()
        return []
    
    def get_medicines_list(self):
        """Get list of all medicines"""
        if self.medicine_data is not None:
            return self.medicine_data['Medicine Name'].unique().tolist()
        return []
    
    def search_medicine_by_name(self, name):
        """Search for medicine by name"""
        if self.medicine_data is not None:
            return self.medicine_data[
                self.medicine_data['Medicine Name'].str.contains(name, case=False, na=False)
            ]
        return pd.DataFrame()
    
    def search_disease_by_name(self, name):
        """Search for disease by name"""
        if self.precaution_data is not None:
            return self.precaution_data[
                self.precaution_data['Disease'].str.contains(name, case=False, na=False)
            ]
        return pd.DataFrame()
