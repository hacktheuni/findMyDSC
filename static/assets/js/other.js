document.addEventListener('DOMContentLoaded', (event) => {

    let table = document.getElementById('myTable');
    let rows = table.getElementsByTagName('tr');
    let rowCount = rows.length - 2;
    document.getElementById('rowCount').innerText = `${rowCount}`;
});


let sortDirections = Array(8).fill(false); // Track sort directions for each column

function filterSearch() {
    let searchInput = document.getElementById('search').value.toLowerCase();
    let table = document.getElementById('myTable');
    let rows = table.getElementsByTagName('tr');
    let columnSearches = table.querySelectorAll('thead tr:nth-child(2) input, thead tr:nth-child(2) select');
    let columnSearchValues = Array.from(columnSearches).map(input => input.value.toLowerCase());
    let visibleRowCount = 0;

    for (let i = 2; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        let match = false;

        if (searchInput) {
            for (let j = 0; j < cells.length; j++) {
                if (cells[j].innerText.toLowerCase().includes(searchInput)) {
                    match = true;
                    break;
                }
            }
        } else {
            match = true;
        }

        for (let col = 0; col < columnSearchValues.length; col++) {
            if (columnSearchValues[col] && !cells[col].innerText.toLowerCase().includes(columnSearchValues[col])) {
                match = false;
                break;
            }
        }

        if (match) {
            rows[i].style.display = '';
            visibleRowCount++;
        } else {
            rows[i].style.display = 'none';
        }
    }

    // Display the count of visible rows
    document.getElementById('rowCount').innerText = `${visibleRowCount}`;
}


function sortTable(columnIndex) {
    let table = document.getElementById('myTable');
    let rows = Array.from(table.getElementsByTagName('tr')).slice(2); // Skip the header rows
    let direction = sortDirections[columnIndex] ? 1 : -1;

    rows.sort((a, b) => {
        let cellA = a.getElementsByTagName('td')[columnIndex].innerText.toLowerCase();
        let cellB = b.getElementsByTagName('td')[columnIndex].innerText.toLowerCase();

        if (cellA < cellB) return -1 * direction;
        if (cellA > cellB) return 1 * direction;
        return 0;
    });

    sortDirections[columnIndex] = !sortDirections[columnIndex]; // Toggle sort direction

    for (let i = 0; i < rows.length; i++) {
        table.getElementsByTagName('tbody')[0].appendChild(rows[i]);
    }
}

