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
  allowEmpty: false,

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
    {title: 'forceX', type: 'numeric', format: '0.0'},
    {title: 'forceY', type: 'numeric', format: '0.0'}
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

  allowEmpty: false,
  data: [
  [1, 2, 1],
  [1, 3, 1],
  [2, 4, 1],
  [3, 4, 1],
  [2, 3, 1],
  [1, 4, 1]
  ],
  columns: [
    {title: 'Point1', type: 'numeric'},
    {title: 'Point2', type: 'numeric'},
    {title: 'constant',
      type: 'numeric',
      format: '0.0',
      validator: /^[0-9]+(\.[0-9]{1,4})?$/
    }],
  rowHeaders: true,
  enterBeginsEditing: false
});


// 自動更新
var count = 0;
$(function() {
	update();
	//関数update()を2000ミリ秒間隔で呼び出す
	setInterval("update()", 4000);

});

function update() {
  var node = JSON.stringify(table_node.getData());
  var spring = JSON.stringify(table_spring.getData());
  var data = JSON.stringify(node + spring);
  $.ajax({
    type : 'post',
    url : '/post',
    data : data,
    contentType: 'application/JSON',
    scriptCharset: 'utf-8',
  })
  .always(function(res) {
    //これはクロスオリジン制限で弾かれるため、「success」「done」ではダメ。
    //No 'Access-Control-Allow-Origin' header is present on the requested resource.
    count++;
    $('show_result').append($('#show_result').html(res));
    $('#show_result').html(res);
  });
};
