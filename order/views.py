from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from order.models import *
from django.db import transaction
from django.db.models import Sum, F, Q
from django.http import HttpResponse, FileResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import JsonResponse
from decimal import Decimal


# Create your views here.

@login_required(login_url = '/login/')
def add_order(request, client_id):
    context = {'page':'Add Order'}
    client_details = Client.objects.get(client_id = client_id)
    client_details.first_name = client_details.first_name.title()
    client_details.last_name = client_details.last_name.title()

    if request.method == "POST":
        # try:
            with transaction.atomic():
                vehicle_no = request.POST.get('vehicle_no')
                order_date = request.POST.get('orderdate')
                items_name = [item for item in request.POST.getlist('item_name[]') if item.strip()]
                quantity = [qty for qty in request.POST.getlist('quantity[]') if qty.strip()]
                rate = [rate for rate in request.POST.getlist('rate[]') if rate.strip()]
                units = [unit for unit in request.POST.getlist('units[]') if unit.strip()]
                weight = request.FILES.get('weight')
                
                if len(items_name) == len(quantity) and len(quantity) == len(rate):
                    new_order = Order.objects.create(client_id=client_details,
                                         order_date=order_date                                         
                                        )
                    # context['post_data'] = request.POST
                    # print("context data: ",context['post_data'])
                    total = 0
                    for x in range(len(items_name)):
                        if vehicle_no is None:
                            OrderItems.objects.create(order_id = new_order,
                                                item_name = items_name[x],
                                                quantity = Decimal(quantity[x]),
                                                rate = Decimal(rate[x]),
                                                units = units[x]                                                
                                                )
                        else:
                            OrderItems.objects.create(order_id = new_order,
                                                item_name = items_name[x],
                                                quantity = Decimal(quantity[x]),
                                                rate = Decimal(rate[x]),
                                                units = units[x],
                                                truck_number = vehicle_no[x]                                              
                                                )
                        total += Decimal(quantity[x]) * Decimal(rate[x])
                        # print(total)
                        
                    Payment.objects.create(order_id= new_order,
                                           status = 'Dr',
                                           amount = total
                                           )
                    
                    new_order.weight = weight
                    new_order.save()         
                    return render(request,'test2.html')
                
        # except Exception as e:
        #     return render(request,"test2.html",{'error':f"Error while storing data. {str(e)}"})       
    else:
         
        return render(request,'addorder.html',{"client_details":client_details})    



@login_required(login_url = '/login/')
def all_orders(request):
    orders = Order.objects.annotate(total_price = Sum(F("orderitems__quantity") * F("orderitems__rate")))
    for order in orders:
        order.order_date = order.order_date.strftime("%d-%m-%Y")
        
    return render(request, "vieworder.html", {"orders": orders,"page":"View Orders"})

@login_required(login_url = '/login/')
def edit_order(request, order_id):
    order_id = order_id
    return render(request, "editorder.html", {"order_id": order_id, "page": 'Edit'})


@login_required(login_url = '/login/')
def orderdetails(request,order_id):
    try:
        order = Order.objects.filter(order_id=order_id).annotate(
            grand_total=Sum(F("orderitems__quantity") * F("orderitems__rate"))
        ).first()
        
        order.order_date = order.order_date.strftime("%d-%m-%Y")
        
        order_items = OrderItems.objects.filter(order_id=order_id).annotate(
            total_price=F("quantity") * F("rate")  # Item-wise total
        )
        
        # grand_total = orders.aggregate(grand_total=Sum("total_price"))["grand_total"]
                
        return render(request, "orderdetails.html", {"order": order, "order_items": order_items})
    except:
        return render(request, "orderdetails.html", {"error":"Somthing wrong"})
    
@login_required(login_url = '/login/')
def invoice_pdf(request, order_id):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{order_id}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Get page width and height

    # Fetch Order and Order Items
    order = Order.objects.filter(order_id=order_id).annotate(
        grand_total=Sum(F("orderitems__quantity") * F("orderitems__rate"))
    ).first()

    if not order:
        return HttpResponse("Order not found", status=404)

    order.order_date = order.order_date.strftime("%d-%m-%Y")

    order_items = OrderItems.objects.filter(order_id=order_id).annotate(
        total_price=F("quantity") * F("rate")
    )

    # Add Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 50, "Invoice")

    # Add Order Details
    p.setFont("Helvetica", 12)
    y_position = height - 100  # Start from here

    p.drawString(50, y_position, f"Order ID: {order.order_id}")
    p.drawString(400, y_position, f"Date: {order.order_date}")
    
    y_position -= 20  # Move down
    p.drawString(50, y_position, f"Customer: {order.first_name} {order.last_name}")
    
    y_position -= 20
    p.drawString(50, y_position, f"Mobile: {order.mobile}")

    y_position -= 20
    p.drawString(50, y_position, f"Email: {order.email}")

    y_position -= 20
    p.drawString(50, y_position, f"City: {order.city}, {order.state} - {order.pincode}")

    y_position -= 40  # Add more space before the table

    # Define Table Data (Headers + Rows)
    data = [["Item Name", "Rate", "Quantity", "Total"]]

    for item in order_items:
        data.append([
            item.item_name,
            f"{item.rate:.2f}",
            f"{item.quantity:.2f}",
            f"{item.total_price:.2f}",
        ])

    # Define Table Position
    table_x = 50

    # Create Table Object
    table = Table(data, colWidths=[150, 100, 100, 100])

    # Apply Table Styles (Borders, Alignments, Padding)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Border for all cells
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header background
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Header text color
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center align text
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold headers
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),  # Regular font for items
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),  # Padding for headers
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),  # Padding for rows
    ]))

    # Draw Table on Canvas
    table.wrapOn(p, width, height)
    table.drawOn(p, table_x, y_position - len(order_items) * 20)  # Shift table down

    # Grand Total
    y_position -= (len(order_items) + 2) * 20  # Adjust position after the table
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y_position, f"Grand Total: {order.grand_total:.2f}")

    # Save the PDF
    p.showPage()
    p.save()

    return response

    
def all_invoice_pdf(request,order_id):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{order_id}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Get page width and height

    # Fetch Order and Order Items
    order = Order.objects.filter(order_id=order_id).annotate(
        grand_total=Sum(F("orderitems__quantity") * F("orderitems__rate"))
    ).first()

    if not order:
        return HttpResponse("Order not found", status=404)

    order.order_date = order.order_date.strftime("%d-%m-%Y")

    order_items = OrderItems.objects.filter(order_id=order_id).annotate(
        total_price=F("quantity") * F("rate")
    )

    # Add Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 50, "Invoice")

    # Add Order Details
    p.setFont("Helvetica", 12)
    y_position = height - 100  # Start from here

    p.drawString(50, y_position, f"Order ID: {order.order_id}")
    p.drawString(400, y_position, f"Date: {order.order_date}")
    
    y_position -= 20  # Move down
    p.drawString(50, y_position, f"Customer: {order.first_name} {order.last_name}")
    
    y_position -= 20
    p.drawString(50, y_position, f"Mobile: {order.mobile}")

    y_position -= 20
    p.drawString(50, y_position, f"Email: {order.email}")

    y_position -= 20
    p.drawString(50, y_position, f"City: {order.city}, {order.state} - {order.pincode}")

    y_position -= 40  # Add more space before the table

    # Define Table Data (Headers + Rows)
    data = [["Item Name", "Rate", "Quantity", "Total"]]

    for item in order_items:
        data.append([
            item.item_name,
            f"{item.rate:.2f}",
            f"{item.quantity:.2f}",
            f"{item.total_price:.2f}",
        ])

    # Define Table Position
    table_x = 50

    # Create Table Object
    table = Table(data, colWidths=[150, 100, 100, 100])

    # Apply Table Styles (Borders, Alignments, Padding)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Border for all cells
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header background
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Header text color
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center align text
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold headers
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),  # Regular font for items
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),  # Padding for headers
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),  # Padding for rows
    ]))

    # Draw Table on Canvas
    table.wrapOn(p, width, height)
    table.drawOn(p, table_x, y_position - len(order_items) * 20)  # Shift table down

    # Grand Total
    y_position -= (len(order_items) + 2) * 20  # Adjust position after the table
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y_position, f"Grand Total: {order.grand_total:.2f}")

    # Save the PDF
    p.showPage()
    p.save()

    return response

def live_search(request):
    query = request.GET.get("query", "").strip()
    search_date = request.GET.get("searchdate", "").strip()
    results = []
    order_filter = Q()
    # print(query)
    
    orders = Order.objects.annotate(
        total_price=Sum(F("orderitems__quantity") * F("orderitems__rate"))
    )
    
    if query:
        orders = orders.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    
    if search_date:
       orders = orders.filter(order_date=search_date)
         
    
    results = [
            {"order_id": order.order_id,
             "order_date": order.order_date.strftime("%d-%m-%Y") if order.order_date else "",
             "customer_name": order.first_name +" "+ order.last_name,
             "mobile": order.mobile,
             "email":order.email,
             "city":order.city,
             "total_price":order.total_price}
            for order in orders
        ]
       
    if "generate_pdf" in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="orders.pdf"'

        p = canvas.Canvas(response, pagesize=landscape(letter))
        width, height = landscape(letter)
        p.setFont("Helvetica", 12)

        # Add Title
        p.setFont("Helvetica-Bold", 20)
        p.drawString(200, height - 50, "Orders")

        # Add Order Details
        p.setFont("Helvetica", 12)
        y_position = height - 90  # Adjust y_position to leave space between title and table

        data = [["Order ID", "Order Date", "Customer Name", "Mobile", "Email", "City", "Total amt"]]
        for order in results:
            data.append([
                order['order_id'],
                order['order_date'],
                order['customer_name'],
                order['mobile'],
                order['email'],
                order['city'],
                f"{order['total_price']:.2f}"
            ])

        table_x = 50

        table = Table(data, colWidths=[50, 80, 150, 100, 150, 80, 100])

        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Border for all cells
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header background
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Header text color
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center align text
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold headers
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),  # Regular font for items
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),  # Padding for headers
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),  # Padding for rows
        ]))

        table.wrapOn(p, width, height)
        table.drawOn(p, table_x, y_position - 40)  # Adjust y_position further to ensure proper spacing

        p.showPage()
        p.save()
        return response
    
    return JsonResponse({"results": results})


def delete_order(request):
    pass



def add_client(request):
    context = {'page':'New client'}
    if request.method == "POST":
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        date_of_birth = request.POST.get('birthdate')
        gender = request.POST.get('gender')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        line3 = request.POST.get('line3')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        
        Client.objects.create(first_name=first_name,
                              last_name=last_name,
                              gender=gender,
                              date_of_birth=date_of_birth,
                              mobile=mobile,
                              email=email,
                              line1=line1,
                              line2=line2,
                              line3=line3,
                              city=city,
                              state=state,
                              pincode=pincode)
        return redirect('client')
        
    else:
        return render(request,"newclient.html",context)

def client_list(request):
    context = {'page':'Client List'}
    client_list = Client.objects.all()
    context.update({"client_list":client_list})
    return render(request,"clientlist.html", context)

def test(request):
    oder_detail = Order.objects.get(order_id = 8)
    print(oder_detail)
    return render(request,'test2.html',{'oder_detail':oder_detail})

