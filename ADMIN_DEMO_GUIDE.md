# Admin Panel Demo Guide

## Overview
The admin panel now has **two tabs**:
1. **Tab 1: Manage Projects** - View, add, edit, delete, and upload projects via Excel
2. **Tab 2: Manage Problems** - View problem details and update step statuses

---

## Tab 1: Manage Projects

### Features:
- ✅ **Add New Project** - Form to manually add projects
- ✅ **Edit Project** - Click "Edit" button to modify existing projects
- ✅ **Delete Project** - Delete projects (blocked if they have associated problems)
- ✅ **Upload Excel** - Bulk upload projects from Excel file

### Excel Upload Format:
Create an Excel file (.xlsx or .xls) with the following columns:

| Project Number | Project Name | Manager Name | Customer Name | Quantity |
|----------------|--------------|--------------|---------------|----------|
| PRJ-001        | Project A    | John Doe     | Acme Corp     | 100      |
| PRJ-002        | Project B    | Jane Smith   | Tech Inc      | 50       |

**Important Notes:**
- First row is treated as header (will be skipped)
- Manager Name and Customer Name must match existing records in the database
- If Project Number exists, it will UPDATE the existing project
- If Project Number is new, it will CREATE a new project

---

## Tab 2: Manage Problems

### Features:
- ✅ **View Problem Details** - Click on a problem row to expand and see:
  - Components list
  - Problem steps with current status
- ✅ **Update Step Status** - Change status of any problem step using dropdown
- ✅ **Delete Problem** - Remove problems from the system

### Available Status Options:
- Design
- Method
- Purchase
- Manufacturing
- Warehouse
- Shipment And Packing
- Shipment
- On the Spot Action
- Finished
- Cancel
- Waiting

---

## How to Test

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python app.py
```

### 3. Access Admin Panel
- Navigate to: `http://127.0.0.1:5000/admin`
- Or click "Admin" in the navigation menu

### 4. Test Tab 1 (Projects)
1. **Add a Project:**
   - Fill in the form with project details
   - Click "Add Project"
   - Verify it appears in the table

2. **Edit a Project:**
   - Click "Edit" button on any project
   - Modify fields in the modal
   - Click "Save Changes"
   - Verify changes are saved

3. **Upload Excel:**
   - Create an Excel file with the format above
   - Click "Choose File" and select your Excel file
   - Click "Upload Excel"
   - Check success message and verify projects in table

4. **Delete a Project:**
   - Click "Delete" on a project without problems
   - Confirm deletion
   - Verify it's removed from the table

### 5. Test Tab 2 (Problems)
1. **View Problem Details:**
   - Click on any problem row
   - Verify components and steps are displayed

2. **Update Step Status:**
   - Expand a problem to see steps
   - Change status using the dropdown
   - Verify status updates immediately

3. **Delete a Problem:**
   - Expand a problem
   - Click "Delete Problem" button
   - Confirm deletion
   - Verify problem is removed

---

## Sample Excel File

You can create a test Excel file with this data:

```
Project Number | Project Name      | Manager Name | Customer Name | Quantity
PRJ-2024-001  | Production Line A | Manager 1    | Customer A    | 100
PRJ-2024-002  | Production Line B | Manager 2    | Customer B    | 200
PRJ-2024-003  | Quality Control   | Manager 1    | Customer A    | 50
```

**Note:** Make sure Manager Name and Customer Name match existing records in your database.

---

## File Structure Changes

### Modified Files:
- `backend/app.py` - Updated admin route with tab handling
- `backend/templates/admin.html` - Complete rewrite with tabs
- `backend/requirements.txt` - Added `openpyxl` for Excel support

### New Features:
- Tab navigation system
- Excel upload with validation
- Project edit modal
- Problem step status updates
- Improved UI with TailwindCSS

---

## Next Steps (For Future Enhancement)

You mentioned you'll provide details later. Here are some areas that can be customized:

1. **Excel Format Customization:**
   - Change column order
   - Add more fields
   - Custom validation rules

2. **Project Editing:**
   - Add more editable fields
   - Change validation rules
   - Add audit logging

3. **Problem Management:**
   - Add more problem-level fields
   - Bulk status updates
   - Export functionality
   - Advanced filtering

4. **UI Enhancements:**
   - Add search/filter
   - Pagination
   - Sorting
   - Export to PDF/Excel

---

## Troubleshooting

### Excel Upload Issues:
- **"Manager not found"** - Ensure manager name exactly matches database
- **"Customer not found"** - Ensure customer name exactly matches database
- **"Missing required fields"** - Check that all columns have values

### Edit Modal Not Showing:
- Check browser console for JavaScript errors
- Ensure all required fields are filled

### Status Not Updating:
- Check database connection
- Verify step_id is correct
- Check browser console for errors

---

## Demo Ready! 🚀

The system is now ready for testing. All core functionality is implemented and working.

