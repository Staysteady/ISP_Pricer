import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

from app.utils.cost_calculator import CostCalculator

def machine_settings():
    """Machine settings UI component."""
    st.subheader("Machine Settings")
    st.write("Configure machine wattage, electricity rates, and process times.")
    
    # Initialize the cost calculator
    calculator = CostCalculator()
    
    # Create tabs for different settings
    tabs = st.tabs([
        "Machines & Electricity", 
        "Process Times", 
        "Testing & Simulation"
    ])
    
    # Machines & Electricity tab
    with tabs[0]:
        machine_electricity_settings(calculator)
    
    # Process Times tab
    with tabs[1]:
        process_time_settings(calculator)
    
    # Testing & Simulation tab
    with tabs[2]:
        cost_simulation(calculator)

def machine_electricity_settings(calculator):
    """UI for managing machines and electricity rates."""
    st.write("Configure machine wattage and electricity rates")
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Print Machines")
        
        # Get current print machines
        print_machines = calculator.settings.get("print_machines", [])
        
        # Display each machine with an editable form
        for i, machine in enumerate(print_machines):
            with st.expander(f"{machine['name']} ({machine['wattage']}W)"):
                name = st.text_input(f"Machine Name", value=machine["name"], key=f"print_machine_name_{i}")
                wattage = st.number_input(f"Wattage (W)", value=machine["wattage"], min_value=1, key=f"print_machine_wattage_{i}")
                description = st.text_input(f"Description", value=machine.get("description", ""), key=f"print_machine_desc_{i}")
                
                if st.button("Update", key=f"update_print_machine_{i}"):
                    # Update machine
                    machine["name"] = name
                    machine["wattage"] = wattage
                    machine["description"] = description
                    
                    # Save settings
                    success, message = calculator.save_settings(calculator.settings)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        # Add new print machine
        with st.expander("Add New Print Machine"):
            new_name = st.text_input("Machine Name", key="new_print_machine_name")
            new_wattage = st.number_input("Wattage (W)", value=400, min_value=1, key="new_print_machine_wattage")
            new_description = st.text_input("Description", key="new_print_machine_desc")
            
            if st.button("Add Machine", key="add_print_machine"):
                if new_name:
                    # Add new machine
                    print_machines.append({
                        "name": new_name,
                        "wattage": new_wattage,
                        "description": new_description
                    })
                    
                    # Save settings
                    calculator.settings["print_machines"] = print_machines
                    success, message = calculator.save_settings(calculator.settings)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Machine name is required")
    
    with col2:
        st.subheader("Embroidery Machines")
        
        # Get current embroidery machines
        embroidery_machines = calculator.settings.get("embroidery_machines", [])
        
        # Display each machine with an editable form
        for i, machine in enumerate(embroidery_machines):
            with st.expander(f"{machine['name']} ({machine['wattage']}W)"):
                name = st.text_input(f"Machine Name", value=machine["name"], key=f"emb_machine_name_{i}")
                wattage = st.number_input(f"Wattage (W)", value=machine["wattage"], min_value=1, key=f"emb_machine_wattage_{i}")
                description = st.text_input(f"Description", value=machine.get("description", ""), key=f"emb_machine_desc_{i}")
                
                if st.button("Update", key=f"update_emb_machine_{i}"):
                    # Update machine
                    machine["name"] = name
                    machine["wattage"] = wattage
                    machine["description"] = description
                    
                    # Save settings
                    success, message = calculator.save_settings(calculator.settings)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        # Add new embroidery machine
        with st.expander("Add New Embroidery Machine"):
            new_name = st.text_input("Machine Name", key="new_emb_machine_name")
            new_wattage = st.number_input("Wattage (W)", value=500, min_value=1, key="new_emb_machine_wattage")
            new_description = st.text_input("Description", key="new_emb_machine_desc")
            
            if st.button("Add Machine", key="add_emb_machine"):
                if new_name:
                    # Add new machine
                    embroidery_machines.append({
                        "name": new_name,
                        "wattage": new_wattage,
                        "description": new_description
                    })
                    
                    # Save settings
                    calculator.settings["embroidery_machines"] = embroidery_machines
                    success, message = calculator.save_settings(calculator.settings)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Machine name is required")
    
    # Electricity rate settings
    st.subheader("Electricity Rate")
    
    # Get current electricity rate
    electricity_rate = calculator.settings.get("electricity_rate", {"cost_per_kwh": 0.4, "last_updated": datetime.now().strftime("%Y-%m-%d")})
    
    # Create a form for updating the electricity rate
    col1, col2 = st.columns(2)
    
    with col1:
        cost_per_kwh = st.number_input(
            "Cost per kWh (£)", 
            value=float(electricity_rate.get("cost_per_kwh", 0.4)),
            min_value=0.01,
            format="%.3f",
            step=0.001
        )
    
    with col2:
        st.write(f"Last Updated: {electricity_rate.get('last_updated', 'Never')}")
        
        if st.button("Update Electricity Rate"):
            success, message = calculator.update_electricity_rate(cost_per_kwh)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def process_time_settings(calculator):
    """UI for managing process times."""
    st.write("Configure process times for different printing and embroidery processes")
    
    # Get current process times
    process_times = calculator.settings.get("process_times", {"print": {}, "embroidery": {}})
    
    # Create tabs for print and embroidery process times
    process_tab1, process_tab2 = st.tabs(["Print Process Times", "Embroidery Process Times"])
    
    # Print process times
    with process_tab1:
        st.subheader("Print Process Times")
        
        # Get print process times
        print_times = process_times.get("print", {})
        
        # Create a dataframe for easier editing
        if print_times:
            process_names = list(print_times.keys())
            process_values = list(print_times.values())
            
            df = pd.DataFrame({
                "Process Name": process_names,
                "Time (minutes)": process_values
            })
            
            # Edit the dataframe
            edited_df = st.data_editor(
                df,
                column_config={
                    "Process Name": st.column_config.TextColumn("Process Name"),
                    "Time (minutes)": st.column_config.NumberColumn("Time (minutes)", min_value=0.1, format="%.1f")
                },
                num_rows="dynamic",
                use_container_width=True
            )
            
            # Save button
            if st.button("Save Print Process Times"):
                # Convert dataframe back to dictionary
                new_print_times = {}
                for _, row in edited_df.iterrows():
                    process_name = row["Process Name"]
                    if process_name:  # Skip empty rows
                        new_print_times[process_name] = row["Time (minutes)"]
                
                # Update settings
                process_times["print"] = new_print_times
                calculator.settings["process_times"] = process_times
                success, message = calculator.save_settings(calculator.settings)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            # Default values if none exist
            default_processes = {
                "standard_print": 10,
                "standard_bake": 5,
                "standard_press": 10,
                "small_logo_print": 5,
                "small_logo_bake": 2.5,
                "small_logo_press": 5
            }
            
            process_names = list(default_processes.keys())
            process_values = list(default_processes.values())
            
            df = pd.DataFrame({
                "Process Name": process_names,
                "Time (minutes)": process_values
            })
            
            st.data_editor(
                df,
                column_config={
                    "Process Name": st.column_config.TextColumn("Process Name"),
                    "Time (minutes)": st.column_config.NumberColumn("Time (minutes)", min_value=0.1, format="%.1f")
                },
                use_container_width=True
            )
            
            if st.button("Add Default Print Process Times"):
                process_times["print"] = default_processes
                calculator.settings["process_times"] = process_times
                success, message = calculator.save_settings(calculator.settings)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Embroidery process times
    with process_tab2:
        st.subheader("Embroidery Process Times")
        
        # Get embroidery process times
        embroidery_times = process_times.get("embroidery", {})
        
        # Create a dataframe for easier editing
        if embroidery_times:
            process_names = list(embroidery_times.keys())
            process_values = list(embroidery_times.values())
            
            df = pd.DataFrame({
                "Process Name": process_names,
                "Time (minutes)": process_values
            })
            
            # Edit the dataframe
            edited_df = st.data_editor(
                df,
                column_config={
                    "Process Name": st.column_config.TextColumn("Process Name"),
                    "Time (minutes)": st.column_config.NumberColumn("Time (minutes)", min_value=0.1, format="%.1f")
                },
                num_rows="dynamic",
                use_container_width=True
            )
            
            # Save button
            if st.button("Save Embroidery Process Times"):
                # Convert dataframe back to dictionary
                new_embroidery_times = {}
                for _, row in edited_df.iterrows():
                    process_name = row["Process Name"]
                    if process_name:  # Skip empty rows
                        new_embroidery_times[process_name] = row["Time (minutes)"]
                
                # Update settings
                process_times["embroidery"] = new_embroidery_times
                calculator.settings["process_times"] = process_times
                success, message = calculator.save_settings(calculator.settings)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            # Default values if none exist
            default_processes = {
                "small_logo": 10,
                "large_logo": 40
            }
            
            process_names = list(default_processes.keys())
            process_values = list(default_processes.values())
            
            df = pd.DataFrame({
                "Process Name": process_names,
                "Time (minutes)": process_values
            })
            
            st.data_editor(
                df,
                column_config={
                    "Process Name": st.column_config.TextColumn("Process Name"),
                    "Time (minutes)": st.column_config.NumberColumn("Time (minutes)", min_value=0.1, format="%.1f")
                },
                use_container_width=True
            )
            
            if st.button("Add Default Embroidery Process Times"):
                process_times["embroidery"] = default_processes
                calculator.settings["process_times"] = process_times
                success, message = calculator.save_settings(calculator.settings)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def cost_simulation(calculator):
    """UI for testing and simulating costs based on settings."""
    st.subheader("Cost Simulation")
    st.write("Test and simulate costs based on your current settings")
    
    # Create tabs for print and embroidery simulations
    sim_tab1, sim_tab2 = st.tabs(["Print Cost Simulation", "Embroidery Cost Simulation"])
    
    # Print cost simulation
    with sim_tab1:
        st.write("Simulate print costs based on current settings")
        
        # Print type selection
        print_type = st.selectbox(
            "Print Type",
            options=["print_1_small", "print_2_small", "print_large_back_front"],
            format_func=lambda x: {
                "print_1_small": "Small Logo Print",
                "print_2_small": "Two Small Logos Print",
                "print_large_back_front": "Large Back + Front Print"
            }.get(x, x)
        )
        
        # Quantity
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Simulate button
        if st.button("Simulate Print Cost"):
            with st.spinner("Calculating costs..."):
                # Calculate and display the cost breakdown
                cost_data = calculator.calculate_print_cost(print_type, quantity)
                
                if cost_data:
                    # Display cost summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Cost", f"£{cost_data['total_cost']:.2f}")
                    
                    with col2:
                        st.metric("Electricity Cost", f"£{cost_data['total_electricity_cost']:.3f}")
                    
                    with col3:
                        st.metric("Material Cost", f"£{cost_data['total_material_cost']:.3f}")
                    
                    with col4:
                        st.metric("Labor Cost", f"£{cost_data['labor_cost']:.2f}")
                    
                    # Show electricity cost breakdown
                    st.subheader("Electricity Cost Breakdown")
                    
                    # Create a dataframe for electricity costs
                    elec_data = []
                    for item in cost_data['electricity_costs']:
                        elec_data.append({
                            "Process": item['process_name'],
                            "Machine": item['machine_name'],
                            "Time (min)": item['process_time_min'],
                            "Machine Power (W)": item['wattage'],
                            "Energy (kWh)": item['energy_kwh'],
                            "Cost per Run": f"£{item['cost_per_run']:.3f}"
                        })
                    
                    elec_df = pd.DataFrame(elec_data)
                    st.dataframe(elec_df, use_container_width=True)
                    
                    # Show material cost breakdown
                    st.subheader("Material Cost Breakdown")
                    
                    # Create a dataframe for material costs
                    mat_data = []
                    for material, data in cost_data['material_costs'].items():
                        mat_data.append({
                            "Material": material,
                            "Cost per Logo": f"£{data['cost_per_logo']:.3f}",
                            "Total Cost": f"£{data['total_cost']:.3f}"
                        })
                    
                    mat_df = pd.DataFrame(mat_data)
                    st.dataframe(mat_df, use_container_width=True)
                else:
                    st.error("Error calculating costs. Please check your settings.")
    
    # Embroidery cost simulation
    with sim_tab2:
        st.write("Simulate embroidery costs based on current settings")
        
        # Embroidery type selection
        embroidery_type = st.selectbox(
            "Embroidery Type",
            options=["emb_1_small", "emb_1_large", "emb_front_back"],
            format_func=lambda x: {
                "emb_1_small": "Small Logo Embroidery",
                "emb_1_large": "Large Logo Embroidery",
                "emb_front_back": "Front + Back Embroidery"
            }.get(x, x)
        )
        
        # Quantity
        emb_quantity = st.number_input("Quantity", min_value=1, value=1, key="emb_quantity")
        
        # Simulate button
        if st.button("Simulate Embroidery Cost"):
            with st.spinner("Calculating costs..."):
                # Calculate and display the cost breakdown
                cost_data = calculator.calculate_embroidery_cost(embroidery_type, emb_quantity)
                
                if cost_data:
                    # Display cost summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Cost", f"£{cost_data['total_cost']:.2f}")
                    
                    with col2:
                        st.metric("Electricity Cost", f"£{cost_data['total_electricity_cost']:.3f}")
                    
                    with col3:
                        st.metric("Material Cost", f"£{cost_data['total_material_cost']:.3f}")
                    
                    with col4:
                        st.metric("Labor Cost", f"£{cost_data['labor_cost']:.2f}")
                    
                    # Show electricity cost breakdown
                    st.subheader("Electricity Cost Breakdown")
                    
                    # Create a dataframe for electricity costs
                    elec_data = []
                    for item in cost_data['electricity_costs']:
                        elec_data.append({
                            "Process": item['process_name'],
                            "Machine": item['machine_name'],
                            "Time (min)": item['process_time_min'],
                            "Machine Power (W)": item['wattage'],
                            "Energy (kWh)": item['energy_kwh'],
                            "Cost per Run": f"£{item['cost_per_run']:.3f}"
                        })
                    
                    elec_df = pd.DataFrame(elec_data)
                    st.dataframe(elec_df, use_container_width=True)
                    
                    # Show material cost breakdown
                    st.subheader("Material Cost Breakdown")
                    
                    # Create a dataframe for material costs
                    mat_data = []
                    for material, data in cost_data['material_costs'].items():
                        mat_data.append({
                            "Material": material,
                            "Cost per Logo": f"£{data['cost_per_logo']:.3f}",
                            "Total Cost": f"£{data['total_cost']:.3f}"
                        })
                    
                    mat_df = pd.DataFrame(mat_data)
                    st.dataframe(mat_df, use_container_width=True)
                else:
                    st.error("Error calculating costs. Please check your settings.") 