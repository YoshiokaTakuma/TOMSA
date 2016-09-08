// 節点Handsontable
var grid_node = document.getElementById('grid_node');
var table_node = new Handsontable(grid_node, {
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
  [1, 0, 0, 'fix', 0, 0],
  [2, 10, 0, 'fix', 0, 0],
  [3, 0, 10, 'free', 1, 0],
  [4, 10, 10, 'free', 0, 0]
  ],
  columns: [
    {title: 'Point_ID', type: 'numeric'},
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

// ばねHandsontable
var grid_spring = document.getElementById('grid_spring');
var table_spring = new Handsontable(grid_spring, {
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
  [1, 1, 2, 1],
  [2, 1, 3, 1],
  [3, 2, 4, 1],
  [4, 3, 4, 1],
  [5, 2, 3, 0.7071]
  ],
  columns: [
    {title: 'Spring_No', type: 'numeric'},
    {title: 'Point1', type: 'numeric'},
    {title: 'Point2', type: 'numeric'},
    {title: 'constant', type: 'numeric'}
    ],
  rowHeaders: true,
  enterBeginsEditing: false
});



function getdata_node(){
  var node = JSON.stringify(table_node.getData());
  var spring = JSON.stringify(table_spring.getData());
  var data = JSON.stringify(node + spring)
  $.ajax({
  type : 'post',
  url : 'http://127.0.0.1:5000/post',
  data : data,
  contentType: 'application/JSON',
  dataType: 'JSON',
  scriptCharset: 'utf-8'
  }).done(function(res){
  // GET した後の処理
  console.table('dekita')
});;

}


function x(){
  var div = document.getElementById('xxx');
  var newElem = document.createElement('li');
  div.appendChild(newElem);
}
