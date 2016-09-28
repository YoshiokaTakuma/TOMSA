// 節点Handsontable


var node_raw= [
    [0,0,'fix',0,0],
    [1,0,'free',0,0],
    [2,0,'free',0,-1],
    [3,0,'free',0,0],
    [4,0,'fix',0,0],
    [0.5,1,'free',0,0],
    [1.5,1,'free',0,0],
    [2.5,1,'free',0,0],
    [3.5,1,'free',0,0]
    ];

/*
function muri(){
  var node_raw ;
  var foo = $.ajax({
    url: '/tmp/table_data',
    
    success: function (data){
      node_raw = foo.responseText;
      console.log(node_raw)
    }
    
  });
  return node_raw;
}

muri().done(function(data){
  var node_raw = data.responseText;

  return node_raw;
});
*/
// console.log(muri());



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

  data: node_raw,
//  data: muri(),
  columns: [
    {title: 'CorrdiX', type: 'numeric', format: '0.0'},
    {title: 'CorrdiY', type: 'numeric', format: '0.0'},
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




$.ajax({
    url: '/tmp/table_data'
  })
  .done(function (data){
      table_node.destroy();
      node_raw = JSON.parse(data);

      table_node = new Handsontable(grid_node, {
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

        data: node_raw,
        columns: [
          {title: 'CorrdiX', type: 'numeric', format: '0.0'},
          {title: 'CorrdiY', type: 'numeric', format: '0.0'},
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

      })
      .fail(function(){
        console.log('first')
      })

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
    [1,2,20],
    [2,3,20],
    [3,4,20],
    [4,5,20],
    [6,7,20],
    [7,8,20],
    [8,9,20],
    [1,6,20],
    [6,2,20],
    [2,7,20],
    [7,3,20],
    [3,8,20],
    [8,4,20],
    [4,9,20],
    [9,5,20]
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
  var data2 = JSON.stringify(node + spring);
  $.ajax({
    type : 'post',
    url : '/post',
    data : data2,
    contentType: 'application/JSON',
    scriptCharset: 'utf-8',
  })
  .always(function(res) {
    //これはクロスオリジン制限で弾かれるため、「success」「done」ではダメ。
    //No 'Access-Control-Allow-Origin' header is present on the requested resource.
    
    $('show_result').append($('#show_result').html(res));
    $('#show_result').html(res);
    
    /*
    $.ajax({
      url: '/tmp/table_data',
      success: function(data){
        var test = data;
        console.log(test);
      
      },
    });
    */
  });
  
  count++;
};

