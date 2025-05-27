$(document).ready(function(){
    $("#addrow").click(function(){
        $("table tbody tr").last().after(
            '<tr>'+
                        '<td><input class="form-control" type="text" id="" name="item_name[]" placeholder=""></td>'+
                        '<td><input class="form-control" type="number" id="" name="rate[]" placeholder="" min=0 step="0.01"></td>'+
                        '<td><input class="form-control" type="number" id="" name="quantity[]" placeholder="" min=0 step="0.01"></td>'+
                        '<td><select class="form-control" name="units[]" id="">'+
                                '<option value="" selected>Select Unit</option>'+
                                '<option value="KG">KG</option>'+
                                '<option value="GM">GRAM</option>'+
                                '<option value="TON">TON</option>'+
                                '<option value="PCS">PCS</option>'+
                                '<option value="LTR">LTR</option>'+
                            '</select></td>'+
                            '<td><input class="form-control" type="number" id="" name="total[]" placeholder="" min=0 disabled></td>'+
                            '<td><input  class="form-input" type="text" name="vehicle_no[]"></td>'+
                            '<td><label class="form-input" style="cursor: pointer;"><i class="fa-solid fa-upload">'+
                            '</i><input type="file" name="weight[]" style="display: none;"></label></td>'+
            '</tr>'
        );
    });

});

function updateGrandTotal() {
    let grandTotal = 0;

    $('input[name="total[]"]').each(function() {
        grandTotal += parseFloat($(this).val()) || 0;
    });

    // Display sum in an input field
    $('input[name="grandtotal"]').val(grandTotal.toFixed(2));
}

$(document).on("input", 'input[name="quantity[]"], input[name="rate[]"]', function() {
    
        let row = $(this).closest("tr");
        let quantity = parseFloat(row.find('input[name="quantity[]"]').val()) || 0;
        let rate = parseFloat(row.find('input[name="rate[]"]').val()) || 0;
        let total = (quantity * rate).toFixed(2);;

        row.find('input[name="total[]"]').val(total); 
        
        updateGrandTotal();
});

$(document).ready(function() {
    function fetchResults(generatePdf = false){
        let query = $("#search-box").val();
        let searchdate = $("#search-date").val();
        let url = "/livesearch/";
        let data = { query: query, searchdate: searchdate };
            if(generatePdf) {
                data.generate_pdf = true;
                url += "?" + $.param(data);
                window.location.href = url;
            }    
            else{ 
                $.ajax({
                    url: "/livesearch/",
                    type:"GET",
                    data: data,
                    dataType: "json",
                    success: function(response) {
                        let results = response.results;
                        let html = "";
                        results.forEach(order => {
                            html += `<tr>
                                        <td>${order.order_id}</td>
                                        <td>${order.order_date}</td>
                                        <td>${ order.customer_name}</td>
                                        <td>${ order.mobile }</td>
                                        <td>${ order.email }</td>
                                        <td>${ order.city }</td>
                                        <td>${ order.total_price }</td>
                                <td>
                                    <a class="btn btn-primary" style="" href="/orderdetails/${order.order_id}">View</a>
                                    <a class="btn btn-warning" href="/editorder/${order.order_id}">Edit</a>
                                    <a class="btn btn-danger" href="/editorder/${order.order_id}">Delete</a>
                                </td>`;
                        });
                        $("#search-results").html(html);
                    }
                });
            }   
        }
    $("#search-box").keyup(function() { fetchResults(); });
    $("#search-date").change(function() { fetchResults(); });
    $("#generate-pdf").click(function() { fetchResults(true); });    
});