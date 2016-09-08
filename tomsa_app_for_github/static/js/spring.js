var grid2 = document.getElementById('grid2');

var table2 = new Handsontable(grid2, {
  contextMenu: {
    items: {
      row_above: {
        name: '上に行を挿入'
      },
      row_below: {
        name: '下に行を挿入'
      },
      remove_row: {
        name: '列を削除'
      }
    }
  },


  data: [
  [1, 2, 1],
  [1, 3, 1],
  [2, 4, 1],
  [3, 4, 1],
  [2, 3, 0.7071]
  ],
  columns: [
    {title: 'Point1', type: 'numeric'},
    {title: 'Point2', type: 'numeric'},
    {title: 'constant', type: 'numeric'}
    ],
  rowHeaders: true,
  enterBeginsEditing: false
});

function getdata_spring(){
  console.table(table2.getData());
}
