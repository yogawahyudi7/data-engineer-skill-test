#!/usr/bin/env python3
"""
Data Warehouse Schema Diagram Generator
Creates a visual PNG diagram of the star schema
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_schema_diagram():
    """Create a visual star schema diagram"""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 16)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Define colors
    fact_color = '#FF6B6B'      # Red for fact table
    dim_color = '#4ECDC4'       # Teal for dimension tables
    border_color = '#2C3E50'    # Dark blue for borders
    text_color = '#2C3E50'      # Dark blue for text
    
    # Title
    ax.text(10, 15.5, 'E-Commerce Data Warehouse - Star Schema', 
            fontsize=24, fontweight='bold', ha='center', color=text_color)
    
    # FACT TABLE - Center
    fact_x, fact_y = 8, 8
    fact_width, fact_height = 4, 3.5
    
    fact_box = FancyBboxPatch(
        (fact_x, fact_y), fact_width, fact_height,
        boxstyle="round,pad=0.1",
        facecolor=fact_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(fact_box)
    
    # Fact table content
    fact_text = """Fact_Orders
    
OrderID (PK)
OrderLineID
DateKey (FK)
CustomerKey (FK)
ProductKey (FK)
StoreKey (FK)
PaymentKey (FK)

≡ MEASURES ≡
Quantity
UnitPrice
LineTotal
Discount
Tax
Profit"""
    
    ax.text(fact_x + fact_width/2, fact_y + fact_height/2, fact_text,
            fontsize=10, ha='center', va='center', color='white', fontweight='bold')
    
    # DIMENSION TABLES
    
    # 1. DIM_CUSTOMER - Top Left
    customer_x, customer_y = 1, 12
    customer_width, customer_height = 3.5, 2.8
    
    customer_box = FancyBboxPatch(
        (customer_x, customer_y), customer_width, customer_height,
        boxstyle="round,pad=0.1",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(customer_box)
    
    customer_text = """Dim_Customer

CustomerKey (PK)
CustomerID
FirstName
LastName
Email
Phone
Address
City, State
Country
CustomerSegment
LifetimeValue
SCD Type 2"""
    
    ax.text(customer_x + customer_width/2, customer_y + customer_height/2, customer_text,
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # 2. DIM_PRODUCT - Top Right
    product_x, product_y = 15.5, 12
    product_width, product_height = 3.5, 2.8
    
    product_box = FancyBboxPatch(
        (product_x, product_y), product_width, product_height,
        boxstyle="round,pad=0.1",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(product_box)
    
    product_text = """Dim_Product

ProductKey (PK)
ProductID
ProductName
CategoryL1/L2/L3
Brand
UnitCost
ListPrice
Color, Size
IsDiscontinued
SCD Type 2"""
    
    ax.text(product_x + product_width/2, product_y + product_height/2, product_text,
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # 3. DIM_DATE - Bottom Left
    date_x, date_y = 1, 3
    date_width, date_height = 3.5, 2.8
    
    date_box = FancyBboxPatch(
        (date_x, date_y), date_width, date_height,
        boxstyle="round,pad=0.1",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(date_box)
    
    date_text = """Dim_Date

DateKey (PK)
Date
DayOfWeek/Month/Year
Quarter
WeekOfYear
IsWeekend
IsHoliday
FiscalYear
Season"""
    
    ax.text(date_x + date_width/2, date_y + date_height/2, date_text,
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # 4. DIM_STORE - Bottom Right
    store_x, store_y = 15.5, 3
    store_width, store_height = 3.5, 2.8
    
    store_box = FancyBboxPatch(
        (store_x, store_y), store_width, store_height,
        boxstyle="round,pad=0.1",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(store_box)
    
    store_text = """Dim_Store

StoreKey (PK)
StoreID
StoreName
StoreType
Address
City, State, Country
Region, District
ManagerName
SquareFootage
IsActive"""
    
    ax.text(store_x + store_width/2, store_y + store_height/2, store_text,
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # 5. DIM_PAYMENT - Right Center
    payment_x, payment_y = 15.5, 7.5
    payment_width, payment_height = 3.5, 2
    
    payment_box = FancyBboxPatch(
        (payment_x, payment_y), payment_width, payment_height,
        boxstyle="round,pad=0.1",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=2
    )
    ax.add_patch(payment_box)
    
    payment_text = """Dim_Payment

PaymentKey (PK)
PaymentMethod
PaymentType
CardType
ProcessorName
IsSecure
ProcessingFee"""
    
    ax.text(payment_x + payment_width/2, payment_y + payment_height/2, payment_text,
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # RELATIONSHIP ARROWS
    arrow_style = dict(arrowstyle='->', lw=2, color=border_color)
    
    # Customer to Fact
    ax.annotate('', xy=(fact_x, fact_y + fact_height*0.8), 
                xytext=(customer_x + customer_width, customer_y + customer_height/2),
                arrowprops=arrow_style)
    
    # Product to Fact
    ax.annotate('', xy=(fact_x + fact_width, fact_y + fact_height*0.8), 
                xytext=(product_x, product_y + product_height/2),
                arrowprops=arrow_style)
    
    # Date to Fact
    ax.annotate('', xy=(fact_x, fact_y + fact_height*0.2), 
                xytext=(date_x + date_width, date_y + date_height/2),
                arrowprops=arrow_style)
    
    # Store to Fact
    ax.annotate('', xy=(fact_x + fact_width, fact_y + fact_height*0.2), 
                xytext=(store_x, store_y + store_height/2),
                arrowprops=arrow_style)
    
    # Payment to Fact
    ax.annotate('', xy=(fact_x + fact_width, fact_y + fact_height/2), 
                xytext=(payment_x, payment_y + payment_height/2),
                arrowprops=arrow_style)
    
    # Add relationship labels
    ax.text(6, 12.5, 'Many-to-One', fontsize=8, rotation=-30, color=border_color, fontweight='bold')
    ax.text(13.5, 12.5, 'Many-to-One', fontsize=8, rotation=30, color=border_color, fontweight='bold')
    ax.text(6, 5, 'Many-to-One', fontsize=8, rotation=30, color=border_color, fontweight='bold')
    ax.text(13.5, 5, 'Many-to-One', fontsize=8, rotation=-30, color=border_color, fontweight='bold')
    ax.text(13.5, 8.5, 'Many-to-One', fontsize=8, color=border_color, fontweight='bold')
    
    # Add legend
    legend_x, legend_y = 1, 0.5
    
    # Fact table legend
    fact_legend = FancyBboxPatch(
        (legend_x, legend_y), 1, 0.4,
        boxstyle="round,pad=0.05",
        facecolor=fact_color,
        edgecolor=border_color,
        linewidth=1
    )
    ax.add_patch(fact_legend)
    ax.text(legend_x + 1.2, legend_y + 0.2, 'Fact Table', fontsize=10, va='center', color=text_color)
    
    # Dimension table legend
    dim_legend = FancyBboxPatch(
        (legend_x + 3, legend_y), 1, 0.4,
        boxstyle="round,pad=0.05",
        facecolor=dim_color,
        edgecolor=border_color,
        linewidth=1
    )
    ax.add_patch(dim_legend)
    ax.text(legend_x + 4.2, legend_y + 0.2, 'Dimension Table', fontsize=10, va='center', color=text_color)
    
    # Add design notes
    notes_text = """Design Notes:
• Grain: One row per order line item
• SCD Type 2: Customer & Product dimensions
• Surrogate Keys: Integer-based for performance
• Additive Measures: Quantity, Revenue, Profit
• Partitioning: By DateKey for performance"""
    
    ax.text(6, 1.5, notes_text, fontsize=10, va='top', color=text_color,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#F8F9FA', edgecolor=border_color))
    
    # Save the diagram
    plt.tight_layout()
    plt.savefig('schema_diagram.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('schema_diagram.pdf', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("✅ Schema diagram saved as:")
    print("   - schema_diagram.png (High resolution PNG)")
    print("   - schema_diagram.pdf (Vector PDF)")
    
    return fig

def create_erd_style_diagram():
    """Create an ERD-style diagram with proper relationship notation"""
    
    fig, ax = plt.subplots(1, 1, figsize=(24, 18))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Colors
    header_color = '#2C3E50'
    body_color = '#ECF0F1'
    pk_color = '#F39C12'
    fk_color = '#E74C3C'
    border_color = '#34495E'
    
    # Title
    ax.text(12, 17, 'E-Commerce Data Warehouse - Entity Relationship Diagram', 
            fontsize=26, fontweight='bold', ha='center', color=header_color)
    
    def draw_table(x, y, width, height, title, columns, pk_columns=[], fk_columns=[]):
        """Draw a database table with proper ERD styling"""
        
        # Main table rectangle
        table_rect = patches.Rectangle((x, y), width, height, 
                                     linewidth=2, edgecolor=border_color, 
                                     facecolor=body_color)
        ax.add_patch(table_rect)
        
        # Header rectangle
        header_height = 0.8
        header_rect = patches.Rectangle((x, y + height - header_height), width, header_height,
                                      linewidth=2, edgecolor=border_color,
                                      facecolor=header_color)
        ax.add_patch(header_rect)
        
        # Table title
        ax.text(x + width/2, y + height - header_height/2, title,
                fontsize=12, fontweight='bold', ha='center', va='center', color='white')
        
        # Column entries
        row_height = (height - header_height) / len(columns)
        for i, column in enumerate(columns):
            row_y = y + height - header_height - (i + 1) * row_height
            
            # Determine column color based on type
            if column in pk_columns:
                icon = '🔑 '
                color = pk_color
                weight = 'bold'
            elif column in fk_columns:
                icon = '🔗 '
                color = fk_color
                weight = 'bold'
            else:
                icon = '   '
                color = 'black'
                weight = 'normal'
            
            ax.text(x + 0.1, row_y + row_height/2, f"{icon}{column}",
                    fontsize=9, ha='left', va='center', color=color, fontweight=weight)
    
    # Define table positions and content
    
    # Fact_Orders (center)
    fact_columns = [
        'OrderID (PK)', 'OrderLineID', 'DateKey (FK)', 'CustomerKey (FK)',
        'ProductKey (FK)', 'StoreKey (FK)', 'PaymentKey (FK)',
        '────────────────', 'Quantity', 'UnitPrice', 'LineTotal',
        'Discount', 'Tax', 'ShippingCost', 'UnitCost', 'Profit'
    ]
    draw_table(9, 6, 6, 8, 'Fact_Orders', fact_columns,
               pk_columns=['OrderID (PK)'],
               fk_columns=['DateKey (FK)', 'CustomerKey (FK)', 'ProductKey (FK)', 
                          'StoreKey (FK)', 'PaymentKey (FK)'])
    
    # Dim_Customer (top left)
    customer_columns = [
        'CustomerKey (PK)', 'CustomerID', 'FirstName', 'LastName',
        'Email', 'Phone', 'Address', 'City', 'State', 'PostalCode',
        'Country', 'CustomerSegment', 'LifetimeValue', 'RegistrationDate',
        'EffectiveDate', 'ExpiryDate', 'IsCurrent'
    ]
    draw_table(1, 11, 5, 6, 'Dim_Customer', customer_columns,
               pk_columns=['CustomerKey (PK)'])
    
    # Dim_Product (top right)
    product_columns = [
        'ProductKey (PK)', 'ProductID', 'ProductName', 'ProductDescription',
        'CategoryL1', 'CategoryL2', 'CategoryL3', 'Brand', 'UnitCost',
        'ListPrice', 'Color', 'Size', 'IsDiscontinued', 'LaunchDate',
        'EffectiveDate', 'ExpiryDate', 'IsCurrent'
    ]
    draw_table(18, 11, 5, 6, 'Dim_Product', product_columns,
               pk_columns=['ProductKey (PK)'])
    
    # Dim_Date (bottom left)
    date_columns = [
        'DateKey (PK)', 'Date', 'DayOfWeek', 'DayName', 'DayOfMonth',
        'DayOfYear', 'WeekOfYear', 'Month', 'MonthName', 'Quarter',
        'Year', 'IsWeekend', 'IsHoliday', 'FiscalYear', 'Season'
    ]
    draw_table(1, 1, 5, 6, 'Dim_Date', date_columns,
               pk_columns=['DateKey (PK)'])
    
    # Dim_Store (bottom right)
    store_columns = [
        'StoreKey (PK)', 'StoreID', 'StoreName', 'StoreType',
        'Address', 'City', 'State', 'PostalCode', 'Country',
        'Region', 'District', 'ManagerName', 'OpenDate', 'IsActive'
    ]
    draw_table(18, 1, 5, 6, 'Dim_Store', store_columns,
               pk_columns=['StoreKey (PK)'])
    
    # Dim_Payment (right center)
    payment_columns = [
        'PaymentKey (PK)', 'PaymentMethod', 'PaymentType',
        'CardType', 'ProcessorName', 'IsSecure', 'ProcessingFee'
    ]
    draw_table(18, 8, 5, 3, 'Dim_Payment', payment_columns,
               pk_columns=['PaymentKey (PK)'])
    
    # Draw relationships with proper ERD notation
    def draw_relationship(x1, y1, x2, y2, label='', curve=0):
        """Draw relationship line with crow's foot notation"""
        
        if curve != 0:
            # Curved line
            mid_x = (x1 + x2) / 2 + curve
            mid_y = (y1 + y2) / 2
            ax.plot([x1, mid_x, x2], [y1, mid_y, y2], 'k-', linewidth=2)
        else:
            # Straight line
            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2)
        
        # Many side (crow's foot) - always at fact table
        crow_size = 0.3
        if x2 > x1:  # Pointing right
            ax.plot([x2-crow_size, x2, x2-crow_size], 
                   [y2-crow_size/2, y2, y2+crow_size/2], 'k-', linewidth=2)
        else:  # Pointing left
            ax.plot([x2+crow_size, x2, x2+crow_size], 
                   [y2-crow_size/2, y2, y2+crow_size/2], 'k-', linewidth=2)
        
        # One side (single line) - always at dimension table
        if x1 > x2:  # Pointing right
            ax.plot([x1-0.1, x1-0.1], [y1-crow_size/3, y1+crow_size/3], 'k-', linewidth=3)
        else:  # Pointing left
            ax.plot([x1+0.1, x1+0.1], [y1-crow_size/3, y1+crow_size/3], 'k-', linewidth=3)
        
        # Label
        if label:
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2 + 0.3
            ax.text(label_x, label_y, label, fontsize=8, ha='center', 
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Draw all relationships
    draw_relationship(6, 14, 9, 12, '1:M', curve=1)      # Customer to Orders
    draw_relationship(18, 14, 15, 12, '1:M', curve=-1)   # Product to Orders
    draw_relationship(6, 4, 9, 8, '1:M', curve=1)        # Date to Orders
    draw_relationship(18, 4, 15, 8, '1:M', curve=-1)     # Store to Orders
    draw_relationship(18, 9.5, 15, 10, '1:M')            # Payment to Orders
    
    # Add legend
    legend_y = 0.5
    
    # Legend items
    ax.text(1, legend_y + 1.5, 'Legend:', fontsize=12, fontweight='bold', color=header_color)
    
    # PK legend
    ax.text(1, legend_y + 1, '🔑 Primary Key (PK)', fontsize=10, color=pk_color, fontweight='bold')
    
    # FK legend
    ax.text(1, legend_y + 0.5, '🔗 Foreign Key (FK)', fontsize=10, color=fk_color, fontweight='bold')
    
    # Relationship legend
    ax.text(6, legend_y + 1, 'Relationships:', fontsize=12, fontweight='bold', color=header_color)
    ax.plot([6, 7], [legend_y + 0.5, legend_y + 0.5], 'k-', linewidth=2)
    ax.plot([6.8, 7, 6.8], [legend_y + 0.4, legend_y + 0.5, legend_y + 0.6], 'k-', linewidth=2)
    ax.plot([6.1, 6.1], [legend_y + 0.4, legend_y + 0.6], 'k-', linewidth=3)
    ax.text(7.5, legend_y + 0.5, 'One-to-Many (1:M)', fontsize=10, va='center')
    
    # Save the ERD diagram
    plt.tight_layout()
    plt.savefig('erd_diagram.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('erd_diagram.pdf', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("✅ ERD diagram saved as:")
    print("   - erd_diagram.png (High resolution PNG)")
    print("   - erd_diagram.pdf (Vector PDF)")
    
    return fig

if __name__ == "__main__":
    print("🎨 Creating Data Warehouse Schema Diagrams...")
    print("=" * 50)
    
    # Create star schema diagram
    print("\n📊 Creating Star Schema Diagram...")
    star_fig = create_schema_diagram()
    
    # Create ERD style diagram
    print("\n📋 Creating ERD Style Diagram...")
    erd_fig = create_erd_style_diagram()
    
    print("\n🎉 All diagrams created successfully!")
    print("\nFiles created:")
    print("  1. schema_diagram.png - Star schema visualization")
    print("  2. schema_diagram.pdf - Star schema (vector)")
    print("  3. erd_diagram.png - ERD style diagram")
    print("  4. erd_diagram.pdf - ERD style (vector)")
    
    # Show the diagrams (optional)
    try:
        plt.show()
    except:
        print("\n💡 Diagrams saved to files. Use image viewer to open PNG files.")
