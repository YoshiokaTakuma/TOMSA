var grid = document.getElementById('grid');

var table = new Handsontable(grid, {
  contextMenu: {
    items: {
      row_above: {
        name: '上に行を挿入'
      },
      row_below: {
        name: '下に行を挿入'
      }
    }
  },


  data: [
  [0, 0, 'fix', 0, 0],
  [10, 0, 'fix', 0, 0],
  [0, 10, 'free', 1, 0],
  [10, 10, 'free', 0, 0]
  ],
  columns: [
    {title: 'CorrdiX', type: 'numeric'},
    {title: 'CorrdiY', type: 'numeric'},
    {title: 'support',
      editor: 'select',
      selectOptions: ['free', 'fix']
    },
    {title: 'forceX', type: 'numeric'},
    {title: 'forceY', type: 'numeric'}
    ],
  rowHeaders: true,
  enterBeginsEditing: false
});

function getdata(){
  console.table(table.getData());
}
