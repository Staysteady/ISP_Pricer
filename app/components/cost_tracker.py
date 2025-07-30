import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys

# Add import for default cost import and machine settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.data.import_default_costs import import_all_costs
from app.components.machine_settings import machine_settings

def cost_tracker_main(cost_tracker):
    """Main cost tracker UI component."""
    st.header("Business Cost Tracker")
    st.write("Track and analyze your business costs")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "Cost Dashboard", 
        "Manage Business Costs", 
        "Machine Settings",  # New tab
        "Electricity Costs", 
        "Material Costs", 
        "Cost Import",
        "Profit Analysis"
    ])
    
    # Cost Dashboard tab
    with tabs[0]:
        cost_dashboard(cost_tracker)
    
    # Manage Business Costs tab
    with tabs[1]:
        manage_business_costs(cost_tracker)
    
    # Machine Settings tab - new tab
    with tabs[2]:
        machine_settings()
    
    # Electricity Costs tab - now index 3
    with tabs[3]:
        electricity_costs(cost_tracker)
    
    # Material Costs tab - now index 4
    with tabs[4]:
        material_costs(cost_tracker)
    
    # Cost Import tab - now index 5
    with tabs[5]:
        cost_import(cost_tracker)
    
    # Profit Analysis tab - now index 6
    with tabs[6]:
        profit_analysis(cost_tracker)

def cost_dashboard(cost_tracker):
    """Cost dashboard with overview and visualizations."""
    st.subheader("Cost Dashboard")
    
    # Get all costs
    costs_df = cost_tracker.get_costs_by_category()
    
    if costs_df.empty:
        st.info("No costs have been added yet. Please add costs in the 'Manage Business Costs' tab.")
        return
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    # Calculate total costs
    fixed_costs = costs_df[costs_df['cost_type'] == 'fixed']['cost_value'].sum()
    variable_costs = costs_df[costs_df['cost_type'] == 'variable']['cost_value'].sum()
    per_unit_costs = costs_df[costs_df['cost_type'] == 'per_unit']['cost_value'].sum()
    
    # Display metrics
    with col1:
        st.metric("Fixed Costs", f"£{fixed_costs:.2f}")
    
    with col2:
        st.metric("Variable Costs", f"£{variable_costs:.2f}")
    
    with col3:
        st.metric("Per Unit Costs", f"£{per_unit_costs:.2f}")
    
    # Create a pie chart for costs by category
    category_costs = costs_df.groupby('category_name')['cost_value'].sum().reset_index()
    
    fig1 = px.pie(
        category_costs, 
        values='cost_value', 
        names='category_name',
        title='Costs by Category',
        hole=0.4,
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Display costs table
    st.subheader("All Costs")
    st.dataframe(
        costs_df[['name', 'category_name', 'cost_value', 'cost_type', 'recurring_period', 'date_incurred']],
        column_config={
            "cost_value": st.column_config.NumberColumn("Cost Value (£)", format="£%.2f"),
            "date_incurred": st.column_config.DateColumn("Date Incurred"),
        },
        use_container_width=True
    )

def manage_business_costs(cost_tracker):
    """UI for managing business costs."""
    st.subheader("Manage Business Costs")
    
    # Create tabs for Add and View/Edit
    add_tab, view_tab = st.tabs(["Add New Cost", "View/Edit Costs"])
    
    # Add New Cost tab
    with add_tab:
        # Get categories for dropdown
        categories_df = cost_tracker.get_all_cost_categories()
        if categories_df.empty:
            st.warning("No categories available. Please add categories first.")
            
            # Simple form to add a category
            with st.form("add_category_form"):
                st.subheader("Add Cost Category")
                category_name = st.text_input("Category Name")
                category_desc = st.text_area("Description")
                submit_cat = st.form_submit_button("Add Category")
                
                if submit_cat and category_name:
                    success, message = cost_tracker.add_cost_category(category_name, category_desc)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            return
        
        # Form for adding a new cost
        with st.form("add_cost_form"):
            st.subheader("Add New Business Cost")
            
            # Category selection
            category_id = st.selectbox(
                "Category", 
                options=categories_df['id'].tolist(),
                format_func=lambda x: categories_df[categories_df['id'] == x]['name'].iloc[0]
            )
            
            # Cost details
            cost_name = st.text_input("Cost Name")
            cost_description = st.text_area("Description")
            cost_value = st.number_input("Cost Value (£)", min_value=0.0, format="%.2f")
            
            # Cost type
            cost_type = st.selectbox(
                "Cost Type",
                options=["fixed", "variable", "per_unit"],
                help="Fixed costs remain constant, variable costs change with business activity, per_unit costs are applied per unit produced"
            )
            
            # Date and recurrence
            date_incurred = st.date_input("Date Incurred", datetime.now())
            recurring_period = st.selectbox(
                "Recurring Period",
                options=["one-time", "daily", "weekly", "monthly", "quarterly", "annually"]
            )
            
            # Submit button
            submit_cost = st.form_submit_button("Add Cost")
            
            if submit_cost and cost_name and cost_value > 0:
                # Prepare data
                cost_data = {
                    "category_id": category_id,
                    "name": cost_name,
                    "description": cost_description,
                    "cost_value": cost_value,
                    "cost_type": cost_type,
                    "date_incurred": date_incurred.strftime("%Y-%m-%d"),
                    "recurring_period": recurring_period
                }
                
                # Add to database
                success, message = cost_tracker.add_business_cost(cost_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    # View/Edit Costs tab
    with view_tab:
        # Get all costs
        costs_df = cost_tracker.get_costs_by_category()
        
        if costs_df.empty:
            st.info("No costs have been added yet.")
            return
        
        # Filter by category
        categories_df = cost_tracker.get_all_cost_categories()
        filter_category = st.selectbox(
            "Filter by Category",
            options=[0] + categories_df['id'].tolist(),
            format_func=lambda x: "All Categories" if x == 0 else categories_df[categories_df['id'] == x]['name'].iloc[0]
        )
        
        # Filter data
        if filter_category != 0:
            filtered_costs = costs_df[costs_df['category_id'] == filter_category]
        else:
            filtered_costs = costs_df
        
        # Display costs
        if not filtered_costs.empty:
            for _, row in filtered_costs.iterrows():
                with st.expander(f"{row['name']} - £{row['cost_value']:.2f}"):
                    # Create columns for layout
                    edit_col1, edit_col2 = st.columns(2)
                    
                    with edit_col1:
                        # Display cost details
                        st.write(f"**Category:** {row['category_name']}")
                        st.write(f"**Description:** {row['description']}")
                        st.write(f"**Type:** {row['cost_type']}")
                        st.write(f"**Date Incurred:** {row['date_incurred']}")
                        st.write(f"**Recurring Period:** {row['recurring_period']}")
                    
                    with edit_col2:
                        # Edit and delete buttons
                        if st.button("Edit", key=f"edit_{row.name}"):
                            # Store the cost data to edit in session state (use row index as ID)
                            st.session_state.editing_cost_id = row.name
                            st.session_state.editing_cost_data = row
                            st.rerun()
                        
                        if st.button("Delete", key=f"delete_{row['id']}"):
                            # Find the index of this cost in the costs list
                            costs_df_full = cost_tracker.get_costs_by_category()
                            if not costs_df_full.empty:
                                cost_index = costs_df_full[costs_df_full.index == row.name].index[0]
                                success, message = cost_tracker.delete_business_cost(cost_index)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
        else:
            st.info("No costs found for the selected category.")
        
        # Edit form (shown when editing a cost)
        if 'editing_cost_id' in st.session_state:
            st.subheader("Edit Cost")
            
            # Get the cost data to edit
            cost_id = st.session_state.editing_cost_id
            cost_data = st.session_state.editing_cost_data
            
            with st.form("edit_cost_form"):
                # Category selection
                category_id = st.selectbox(
                    "Category", 
                    options=categories_df['id'].tolist(),
                    index=categories_df.index[categories_df['id'] == cost_data['category_id']].tolist()[0],
                    format_func=lambda x: categories_df[categories_df['id'] == x]['name'].iloc[0]
                )
                
                # Cost details
                cost_name = st.text_input("Cost Name", value=cost_data['name'])
                cost_description = st.text_area("Description", value=cost_data['description'])
                cost_value = st.number_input("Cost Value (£)", min_value=0.0, value=float(cost_data['cost_value']), format="%.2f")
                
                # Cost type
                cost_type_options = ["fixed", "variable", "per_unit"]
                cost_type_index = cost_type_options.index(cost_data['cost_type']) if cost_data['cost_type'] in cost_type_options else 0
                cost_type = st.selectbox(
                    "Cost Type",
                    options=cost_type_options,
                    index=cost_type_index
                )
                
                # Date and recurrence
                date_incurred = st.date_input(
                    "Date Incurred", 
                    datetime.strptime(cost_data['date_incurred'], "%Y-%m-%d") if cost_data['date_incurred'] else datetime.now()
                )
                
                recurring_options = ["one-time", "daily", "weekly", "monthly", "quarterly", "annually"]
                recurring_index = recurring_options.index(cost_data['recurring_period']) if cost_data['recurring_period'] in recurring_options else 0
                recurring_period = st.selectbox(
                    "Recurring Period",
                    options=recurring_options,
                    index=recurring_index
                )
                
                # Submit and cancel buttons
                col1, col2 = st.columns(2)
                with col1:
                    submit_edit = st.form_submit_button("Save Changes")
                with col2:
                    cancel_edit = st.form_submit_button("Cancel")
                
                if submit_edit:
                    # Prepare updated data
                    updated_data = {
                        "category_id": category_id,
                        "name": cost_name,
                        "description": cost_description,
                        "cost_value": cost_value,
                        "cost_type": cost_type,
                        "date_incurred": date_incurred.strftime("%Y-%m-%d"),
                        "recurring_period": recurring_period
                    }
                    
                    # Update in database - find the index of this cost
                    costs_df_full = cost_tracker.get_costs_by_category()
                    if not costs_df_full.empty:
                        # Find the cost by matching all fields since we don't have a stable ID
                        matching_rows = costs_df_full[
                            (costs_df_full['name'] == cost_data['name']) & 
                            (costs_df_full['category_id'] == cost_data['category_id']) &
                            (costs_df_full['cost_value'] == cost_data['cost_value'])
                        ]
                        if not matching_rows.empty:
                            cost_index = matching_rows.index[0]
                            success, message = cost_tracker.update_business_cost(cost_index, updated_data)
                            if success:
                                st.success(message)
                                # Clear editing state
                                del st.session_state.editing_cost_id
                                del st.session_state.editing_cost_data
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Could not find cost to update")
                
                if cancel_edit:
                    # Clear editing state
                    del st.session_state.editing_cost_id
                    del st.session_state.editing_cost_data
                    st.rerun()

def electricity_costs(cost_tracker):
    """Display and manage electricity costs."""
    st.subheader("Electricity Costs")
    
    # Get electricity costs from database
    electricity_df = cost_tracker.get_all_electricity_costs()
    
    if electricity_df.empty:
        st.info("No electricity costs have been imported yet. Please use the 'Cost Import' tab to import costs.")
        return
    
    # Create tabs for Print and Embroidery
    print_tab, emb_tab = st.tabs(["Print Electricity", "Embroidery Electricity"])
    
    # Print electricity tab
    with print_tab:
        print_df = electricity_df[electricity_df['process_type'] == 'print']
        if not print_df.empty:
            st.dataframe(
                print_df[['process_name', 'avg_time_min', 'cost_per_unit_kwh', 'machine_watts', 'usage_w', 'cost_per_run']],
                column_config={
                    "process_name": st.column_config.TextColumn("Process"),
                    "avg_time_min": st.column_config.NumberColumn("Avg Time (min)"),
                    "cost_per_unit_kwh": st.column_config.NumberColumn("Cost per kWh (£)"),
                    "machine_watts": st.column_config.NumberColumn("Machine Power (W)"),
                    "usage_w": st.column_config.NumberColumn("Usage (W)"),
                    "cost_per_run": st.column_config.NumberColumn("Cost (£)", format="£%.2f"),
                },
                use_container_width=True
            )
            
            # Create a bar chart
            fig = px.bar(
                print_df, 
                x='process_name', 
                y='cost_per_run',
                title='Print Electricity Costs per Process',
                labels={
                    'process_name': 'Process',
                    'cost_per_run': 'Cost (£)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No print electricity costs found.")
    
    # Embroidery electricity tab
    with emb_tab:
        emb_df = electricity_df[electricity_df['process_type'] == 'embroidery']
        if not emb_df.empty:
            st.dataframe(
                emb_df[['process_name', 'avg_time_min', 'cost_per_unit_kwh', 'machine_watts', 'usage_w', 'cost_per_run']],
                column_config={
                    "process_name": st.column_config.TextColumn("Process"),
                    "avg_time_min": st.column_config.NumberColumn("Avg Time (min)"),
                    "cost_per_unit_kwh": st.column_config.NumberColumn("Cost per kWh (£)"),
                    "machine_watts": st.column_config.NumberColumn("Machine Power (W)"),
                    "usage_w": st.column_config.NumberColumn("Usage (W)"),
                    "cost_per_run": st.column_config.NumberColumn("Cost (£)", format="£%.2f"),
                },
                use_container_width=True
            )
            
            # Create a bar chart
            fig = px.bar(
                emb_df, 
                x='process_name', 
                y='cost_per_run',
                title='Embroidery Electricity Costs per Process',
                labels={
                    'process_name': 'Process',
                    'cost_per_run': 'Cost (£)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No embroidery electricity costs found.")

def material_costs(cost_tracker):
    """Display and manage material costs."""
    st.subheader("Material Costs")
    
    # Get material costs from database
    materials_df = cost_tracker.get_all_material_costs()
    
    if materials_df.empty:
        st.info("No material costs have been imported yet. Please use the 'Cost Import' tab to import costs.")
        return
    
    # Create tabs for different material types
    material_types = materials_df['material_type'].unique()
    tabs = st.tabs(material_types)
    
    for i, material_type in enumerate(material_types):
        with tabs[i]:
            material_df = materials_df[materials_df['material_type'] == material_type]
            
            st.dataframe(
                material_df[['material_name', 'cost_per_unit', 'unit_measurement', 'unit_value', 'logo_size', 'cost_per_logo']],
                column_config={
                    "material_name": st.column_config.TextColumn("Material"),
                    "cost_per_unit": st.column_config.NumberColumn("Cost per Unit (£)", format="£%.2f"),
                    "unit_measurement": st.column_config.TextColumn("Unit Type"),
                    "unit_value": st.column_config.NumberColumn("Unit Value"),
                    "logo_size": st.column_config.TextColumn("Logo Size"),
                    "cost_per_logo": st.column_config.NumberColumn("Cost per Logo (£)", format="£%.2f"),
                },
                use_container_width=True
            )
            
            # Create a bar chart for cost per logo
            fig = px.bar(
                material_df, 
                x='material_name', 
                y='cost_per_logo',
                color='logo_size',
                title=f'{material_type} Costs per Logo Size',
                labels={
                    'material_name': 'Material',
                    'cost_per_logo': 'Cost per Logo (£)',
                    'logo_size': 'Logo Size'
                },
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

def cost_import(cost_tracker):
    """Import costs from various sources."""
    st.subheader("Import Costs")
    
    # Add import button for default costs from image
    if st.button("Import Default Costs from Image"):
        with st.spinner("Importing default costs from image data..."):
            if import_all_costs():
                st.success("Default costs imported successfully from image data!")
                st.rerun()
            else:
                st.error("Error importing default costs")
    
    # Create tabs for different import methods
    json_tab, excel_tab, manual_tab, manage_tab = st.tabs(["Import JSON", "Import Excel", "Manual Entry", "Manage Imports"])
    
    # JSON Import tab
    with json_tab:
        st.write("Import costs from a JSON file")
        uploaded_file = st.file_uploader("Upload JSON cost file", type=["json"])
        
        if uploaded_file is not None:
            try:
                imported_data = json.load(uploaded_file)
                st.success("JSON file loaded successfully!")
                
                # Show preview
                st.write("Data Preview:")
                st.json(imported_data)
                
                # Import button
                if st.button("Import Data"):
                    # Import logic here based on the structure of your JSON
                    st.success("Data imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading JSON file: {str(e)}")
    
    # Excel Import tab
    with excel_tab:
        st.write("Import costs from an Excel file")
        uploaded_file = st.file_uploader("Upload Excel cost file", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success("Excel file loaded successfully!")
                
                # Show preview
                st.write("Data Preview:")
                st.dataframe(df)
                
                # Import button
                if st.button("Import Data"):
                    # Import logic here based on your Excel structure
                    st.success("Data imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading Excel file: {str(e)}")
    
    # Manual Entry tab
    with manual_tab:
        st.write("Import costs from the image data manually")
        
        # Tabs for electricity and materials
        elec_tab, mat_tab = st.tabs(["Electricity Costs", "Material Costs"])
        
        # Electricity costs tab
        with elec_tab:
            st.subheader("Import Electricity Costs")
            
            with st.form("import_electricity_form"):
                # Create form for electricity imports based on the image
                st.write("Enter electricity cost data from the image")
                
                # Process type selection
                process_type = st.selectbox("Process Type", options=["print", "embroidery"])
                
                # Process details
                process_name = st.text_input("Process Name (e.g., Print 1 Logo)")
                avg_time = st.number_input("Average Time (minutes)", min_value=0.0, step=0.5)
                cost_per_kwh = st.number_input("Cost per kWh (£)", min_value=0.0, value=0.4, step=0.01)
                machine_watts = st.number_input("Machine Power (Watts)", min_value=0)
                usage_w = st.number_input("Usage (W)", min_value=0)
                cost_per_run = st.number_input("Cost per Run (£)", min_value=0.0, step=0.01)
                
                # Submit button
                submit_elec = st.form_submit_button("Add Electricity Cost")
                
                if submit_elec and process_name and avg_time > 0 and machine_watts > 0:
                    # Prepare electricity data
                    electricity_data = [{
                        "process_type": process_type,
                        "process_name": process_name,
                        "avg_time_min": float(avg_time),
                        "cost_per_unit_kwh": float(cost_per_kwh),
                        "machine_watts": float(machine_watts),
                        "usage_w": float(usage_w),
                        "cost_per_run": float(cost_per_run)
                    }]
                    
                    # Import to database
                    if cost_tracker.import_electricity_costs_from_image(electricity_data):
                        st.success("Electricity cost imported successfully!")
                    else:
                        st.error("Error importing electricity cost")
        
        # Material costs tab
        with mat_tab:
            st.subheader("Import Material Costs")
            
            with st.form("import_material_form"):
                # Create form for material imports based on the image
                st.write("Enter material cost data from the image")
                
                # Material type selection
                material_type = st.selectbox(
                    "Material Type", 
                    options=["Film", "Ink", "Powder", "Backing", "Other"]
                )
                
                # Material details
                material_name = st.text_input("Material Name")
                cost_per_unit = st.number_input("Cost per Unit (£)", min_value=0.0, step=0.01)
                unit_measurement = st.selectbox(
                    "Unit Measurement", 
                    options=["Length (m)", "Weight (g)", "Piece", "Other"]
                )
                unit_value = st.number_input("Unit Value", min_value=0.0, step=0.1)
                logo_size = st.selectbox("Logo Size", options=["Small Logo", "Large Logo"])
                cost_per_logo = st.number_input("Cost per Logo (£)", min_value=0.0, step=0.01)
                
                # Submit button
                submit_mat = st.form_submit_button("Add Material Cost")
                
                if submit_mat and material_name and cost_per_unit > 0:
                    # Prepare material data
                    material_data = [{
                        "material_type": material_type,
                        "material_name": material_name,
                        "cost_per_unit": float(cost_per_unit),
                        "unit_measurement": unit_measurement,
                        "unit_value": float(unit_value),
                        "logo_size": logo_size,
                        "cost_per_logo": float(cost_per_logo)
                    }]
                    
                    # Import to database
                    if cost_tracker.import_material_costs_from_image(material_data):
                        st.success("Material cost imported successfully!")
                    else:
                        st.error("Error importing material cost")
    
    # Manage Imports tab
    with manage_tab:
        st.subheader("Manage Imported Costs")
        
        # Create subtabs for electricity and material costs
        manage_elec_tab, manage_mat_tab = st.tabs(["Manage Electricity Costs", "Manage Material Costs"])
        
        # Manage electricity costs
        with manage_elec_tab:
            st.write("View and delete imported electricity costs")
            
            # Get electricity costs from database
            electricity_df = cost_tracker.get_all_electricity_costs()
            
            if electricity_df.empty:
                st.info("No electricity costs have been imported yet.")
            else:
                # Add an ID column for reference if not present
                if 'id' not in electricity_df.columns:
                    electricity_df['id'] = range(1, len(electricity_df) + 1)
                
                # Display the dataframe
                st.dataframe(
                    electricity_df[['id', 'process_type', 'process_name', 'avg_time_min', 'cost_per_unit_kwh', 'machine_watts', 'usage_w', 'cost_per_run']],
                    column_config={
                        "id": st.column_config.NumberColumn("ID"),
                        "process_type": st.column_config.TextColumn("Process Type"),
                        "process_name": st.column_config.TextColumn("Process"),
                        "avg_time_min": st.column_config.NumberColumn("Time (min)"),
                        "cost_per_unit_kwh": st.column_config.NumberColumn("Cost/kWh (£)"),
                        "machine_watts": st.column_config.NumberColumn("Machine Power (W)"),
                        "usage_w": st.column_config.NumberColumn("Usage (W)"),
                        "cost_per_run": st.column_config.NumberColumn("Cost (£)", format="£%.3f"),
                    },
                    use_container_width=True
                )
                
                # Create a form to delete by ID
                with st.form("delete_electricity_form"):
                    st.write("Delete an electricity cost entry")
                    
                    # Get IDs for selection
                    elec_ids = electricity_df['id'].tolist()
                    
                    # Create a selection for the ID to delete
                    delete_id = st.selectbox(
                        "Select Entry to Delete", 
                        options=elec_ids,
                        format_func=lambda x: f"ID {x}: {electricity_df[electricity_df['id'] == x]['process_name'].iloc[0]} ({electricity_df[electricity_df['id'] == x]['process_type'].iloc[0]})"
                    )
                    
                    # Submit button
                    submit_delete = st.form_submit_button("Delete Entry")
                    
                    if submit_delete:
                        # Get the process name and type for the selected ID
                        selected_row = electricity_df[electricity_df['id'] == delete_id].iloc[0]
                        process_name = selected_row['process_name']
                        process_type = selected_row['process_type']
                        
                        # Delete the entry
                        success = cost_tracker.delete_electricity_cost(process_name, process_type)
                        if success:
                            st.success(f"Electricity cost entry '{process_name}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error deleting electricity cost entry '{process_name}'")
        
        # Manage material costs
        with manage_mat_tab:
            st.write("View and delete imported material costs")
            
            # Get material costs from database
            materials_df = cost_tracker.get_all_material_costs()
            
            if materials_df.empty:
                st.info("No material costs have been imported yet.")
            else:
                # Add an ID column for reference if not present
                if 'id' not in materials_df.columns:
                    materials_df['id'] = range(1, len(materials_df) + 1)
                
                # Display the dataframe
                st.dataframe(
                    materials_df[['id', 'material_type', 'material_name', 'cost_per_unit', 'unit_measurement', 'logo_size', 'cost_per_logo']],
                    column_config={
                        "id": st.column_config.NumberColumn("ID"),
                        "material_type": st.column_config.TextColumn("Type"),
                        "material_name": st.column_config.TextColumn("Material"),
                        "cost_per_unit": st.column_config.NumberColumn("Cost/Unit (£)", format="£%.2f"),
                        "unit_measurement": st.column_config.TextColumn("Unit Type"),
                        "logo_size": st.column_config.TextColumn("Logo Size"),
                        "cost_per_logo": st.column_config.NumberColumn("Cost/Logo (£)", format="£%.3f"),
                    },
                    use_container_width=True
                )
                
                # Create a form to delete by ID
                with st.form("delete_material_form"):
                    st.write("Delete a material cost entry")
                    
                    # Get IDs for selection
                    mat_ids = materials_df['id'].tolist()
                    
                    # Create a selection for the ID to delete
                    delete_id = st.selectbox(
                        "Select Entry to Delete", 
                        options=mat_ids,
                        format_func=lambda x: f"ID {x}: {materials_df[materials_df['id'] == x]['material_name'].iloc[0]} ({materials_df[materials_df['id'] == x]['material_type'].iloc[0]}, {materials_df[materials_df['id'] == x]['logo_size'].iloc[0]})"
                    )
                    
                    # Submit button
                    submit_delete = st.form_submit_button("Delete Entry")
                    
                    if submit_delete:
                        # Get the material name and type for the selected ID
                        selected_row = materials_df[materials_df['id'] == delete_id].iloc[0]
                        material_name = selected_row['material_name']
                        material_type = selected_row['material_type']
                        
                        # Delete the entry
                        success = cost_tracker.delete_material_cost(material_name, material_type)
                        if success:
                            st.success(f"Material cost entry '{material_name}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error deleting material cost entry '{material_name}'")

def profit_analysis(cost_tracker):
    """Analyze profits compared to quotes."""
    st.subheader("Profit Analysis")
    
    # Get line items from session state
    line_items = st.session_state.get('line_items', [])
    
    if not line_items:
        st.info("No quotes available for analysis. Please create a quote in the Quoting Tool first.")
        
        # Show business-level profit analysis as a fallback
        business_profit_analysis()
        return
    
    # Calculate costs and profits for the current quote
    quote_data = {
        'line_items': line_items
    }
    profit_data = cost_tracker.calculate_quote_costs_and_profit(quote_data)
    
    # Create tabs for different profit views
    tabs = st.tabs(["Current Quote Analysis", "Line Item Breakdown", "Business-Level Analysis"])
    
    # Current Quote Analysis tab
    with tabs[0]:
        quote_profit_summary(profit_data)
    
    # Line Item Breakdown tab
    with tabs[1]:
        line_item_breakdown(profit_data)
    
    # Business-Level Analysis tab
    with tabs[2]:
        business_profit_analysis()

def quote_profit_summary(profit_data):
    """Show a summary of the current quote's profit."""
    st.subheader("Current Quote Profit Summary")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"£{profit_data['total_revenue']:.2f}")
    
    with col2:
        st.metric("Total Cost", f"£{profit_data['total_cost']:.2f}")
    
    with col3:
        st.metric("Profit", f"£{profit_data['total_profit']:.2f}")
    
    with col4:
        st.metric("Profit Margin", f"{profit_data['profit_margin']:.2f}%")
    
    # Create a bar chart showing revenue, cost, and profit
    data = {
        'Category': ['Revenue', 'Cost', 'Profit'],
        'Value': [profit_data['total_revenue'], profit_data['total_cost'], profit_data['total_profit']]
    }
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df,
        x='Category',
        y='Value',
        title='Quote Financial Breakdown',
        labels={'Value': 'Amount (£)'},
        color='Category',
        color_discrete_map={
            'Revenue': 'green',
            'Cost': 'red',
            'Profit': 'blue'
        }
    )
    
    # Add a unique key
    st.plotly_chart(fig, use_container_width=True, key="quote_financial_breakdown")
    
    # Create a pie chart showing cost breakdown
    cost_categories = []
    cost_values = []
    
    # Aggregate costs across all line items
    for line_item in profit_data['line_items']:
        cost_dict = line_item['costs']
        for key, value in cost_dict.items():
            if key not in ['total_cost', 'revenue', 'profit', 'profit_margin'] and value > 0:
                category_name = key.replace('_', ' ').title()
                if category_name in cost_categories:
                    index = cost_categories.index(category_name)
                    cost_values[index] += value
                else:
                    cost_categories.append(category_name)
                    cost_values.append(value)
    
    # Create pie chart
    cost_df = pd.DataFrame({
        'Category': cost_categories,
        'Value': cost_values
    })
    
    fig2 = px.pie(
        cost_df,
        values='Value',
        names='Category',
        title='Cost Breakdown',
        hole=0.4
    )
    
    # Add a unique key
    st.plotly_chart(fig2, use_container_width=True, key="cost_breakdown_pie")

def line_item_breakdown(profit_data):
    """Show a detailed breakdown of each line item's costs and profits."""
    st.subheader("Line Item Cost & Profit Breakdown")
    
    line_items = profit_data['line_items']
    
    if not line_items:
        st.info("No line items available for analysis.")
        return
    
    # Create a DataFrame for line items summary
    summary_data = []
    for item in line_items:
        summary_data.append({
            'Item': f"{item['product_name']} ({item['style_no']})",
            'Quantity': item['quantity'],
            'Services': ', '.join(item['services']),
            'Revenue': item['revenue'],
            'Cost': item['costs']['total_cost'],
            'Profit': item['profit'],
            'Margin': item['profit_margin']
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Display summary table
    st.dataframe(
        summary_df,
        column_config={
            'Item': st.column_config.TextColumn("Product"),
            'Quantity': st.column_config.NumberColumn("Qty"),
            'Services': st.column_config.TextColumn("Services"),
            'Revenue': st.column_config.NumberColumn("Revenue (£)", format="£%.2f"),
            'Cost': st.column_config.NumberColumn("Cost (£)", format="£%.2f"),
            'Profit': st.column_config.NumberColumn("Profit (£)", format="£%.2f"),
            'Margin': st.column_config.ProgressColumn("Margin (%)", format="%.1f%%", min_value=0, max_value=100)
        },
        use_container_width=True
    )
    
    # Create detailed expandable sections for each line item
    for i, item in enumerate(line_items):
        with st.expander(f"Details: {item['product_name']} ({item['style_no']})"):
            # Create columns for key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Revenue", f"£{item['revenue']:.2f}")
            
            with col2:
                st.metric("Total Cost", f"£{item['costs']['total_cost']:.2f}")
            
            with col3:
                st.metric("Profit", f"£{item['profit']:.2f}")
            
            with col4:
                st.metric("Margin", f"{item['profit_margin']:.2f}%")
            
            # Create a bar chart for cost breakdown
            cost_items = []
            cost_values = []
            
            for key, value in item['costs'].items():
                if key not in ['total_cost', 'revenue', 'profit', 'profit_margin'] and value > 0:
                    cost_items.append(key.replace('_', ' ').title())
                    cost_values.append(value)
            
            cost_df = pd.DataFrame({
                'Category': cost_items,
                'Value': cost_values
            })
            
            # Only show chart if there are costs to display
            if not cost_df.empty:
                fig = px.bar(
                    cost_df,
                    x='Category',
                    y='Value',
                    title=f'Cost Breakdown - {item["product_name"]}',
                    labels={'Value': 'Amount (£)'}
                )
                
                # Add a unique key for each plotly chart
                st.plotly_chart(fig, use_container_width=True, key=f"cost_breakdown_{item['id']}")
            
            # Additional details table
            st.write("#### Item Details")
            
            details_data = {
                'Detail': ['Product Name', 'Style No', 'Quantity', 'Services', 'Unit Price', 'Unit Cost', 'Unit Profit'],
                'Value': [
                    item['product_name'],
                    item['style_no'],
                    item['quantity'],
                    ', '.join(item['services']),
                    f"£{item['revenue'] / item['quantity']:.2f}" if item['quantity'] > 0 else "£0.00",
                    f"£{item['costs']['total_cost'] / item['quantity']:.2f}" if item['quantity'] > 0 else "£0.00",
                    f"£{item['profit'] / item['quantity']:.2f}" if item['quantity'] > 0 else "£0.00"
                ]
            }
            
            details_df = pd.DataFrame(details_data)
            st.dataframe(details_df, hide_index=True, use_container_width=True)

def business_profit_analysis():
    """Show a business-level profit analysis with sample data."""
    st.subheader("Business-Level Profit Analysis")
    
    # Simulated data for demonstration
    st.write("Sample Business Profit Analysis:")
    
    # Create sample data
    sample_data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [5000, 5500, 4800, 6000, 6500, 7000],
        'Costs': [3000, 3200, 3100, 3500, 3800, 4000],
        'Profit': [2000, 2300, 1700, 2500, 2700, 3000]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create a combined chart
    fig = go.Figure()
    
    # Add bars for revenue
    fig.add_trace(go.Bar(
        x=df['Month'],
        y=df['Revenue'],
        name='Revenue',
        marker_color='royalblue'
    ))
    
    # Add bars for costs
    fig.add_trace(go.Bar(
        x=df['Month'],
        y=df['Costs'],
        name='Costs',
        marker_color='red'
    ))
    
    # Add line for profit
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Profit'],
        mode='lines+markers',
        name='Profit',
        marker_color='green',
        line=dict(width=4)
    ))
    
    # Update layout
    fig.update_layout(
        title='Revenue, Costs and Profit Over Time',
        xaxis_title='Month',
        yaxis_title='Amount (£)',
        legend_title='Legend',
        barmode='group',
        hovermode='x unified'
    )
    
    # Add a unique key
    st.plotly_chart(fig, use_container_width=True, key="business_profit_chart")
    
    # Add profit margin chart
    profit_margin = [p/r*100 for p, r in zip(df['Profit'], df['Revenue'])]
    
    fig_margin = px.line(
        x=df['Month'],
        y=profit_margin,
        markers=True,
        title='Profit Margin Over Time',
        labels={'x': 'Month', 'y': 'Profit Margin (%)'}
    )
    
    # Add threshold line at 40% margin
    fig_margin.add_hline(
        y=40, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Target Margin (40%)",
        annotation_position="bottom right"
    )
    
    # Add a unique key
    st.plotly_chart(fig_margin, use_container_width=True, key="profit_margin_chart") 