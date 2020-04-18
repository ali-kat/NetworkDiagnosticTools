const socket = io.connect('http://' + document.domain + ':' + location.port)
const status = document.getElementById("status")
var text = "";
var received = []; 

// taken from: https://www.w3schools.com/howto/howto_js_filter_table.asp
function filter() {
  var input, filter, table, tr, td, cell, i, j;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("daTable");
  tr = table.getElementsByTagName("tr");
  for (i = 1; i < tr.length; i++) {
    tr[i].style.display = "none"; 
    td = tr[i].getElementsByTagName("td");
    for (var j = 0; j < td.length; j++) {
      cell = tr[i].getElementsByTagName("td")[j];
      if (cell) {
        if (cell.innerHTML.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
          break;
        }
      }
    }
  }
}

socket.on("output", function(data){
  received.unshift(data.output)
  if(received.length > 1){
    var i, j;
    text = ""
    for (i = 0; i < received.length; i++) {
      text += '<tr>';
      for (j = 0; j < received[i].length; j++){
        text += '<td>' + received[i][j] + '</td>';
      }
      text += '</tr>';
    } 
    display.innerHTML = text;
  }
})

socket.on("connect", () => {
  status.innerHTML = '<span style="background-color: lightgreen;">connected</span>'
})

socket.on("disconnect", () => {
  status.innerHTML = '<span style="background-color: #ff8383;">disconnected</span>'
})