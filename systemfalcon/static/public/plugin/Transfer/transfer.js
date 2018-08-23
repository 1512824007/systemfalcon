/**
 * Created by Liang on 2017/10/9.
 */
!(function(factory){
    if (typeof define === "function" && (define.amd || define.cmd) && !jQuery) {
        // AMD或CMD
        define([ "jquery" ],factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node/CommonJS
        module.exports = function( root, jQuery ) {
            if ( jQuery === undefined ) {
                if ( typeof window !== 'undefined' ) {
                    jQuery = require('jquery');
                } else {
                    jQuery = require('jquery')(root);
                }
            }
            factory(jQuery);
            return jQuery;
        };
    } else {
        //Browser globals
        factory(jQuery);
    }
})(function($){
    var defaults={
        data:{left:[],right:[]},
        search:'left',
        title:['选择','已选']
    }
    var Transfer = function(element,options){
        var opts = options,//配置
            $document = $(document),
            $obj = $(element),//容器
            _element=$obj[0];
        this.opts=opts;
        //初始化穿梭框
        this.initElement=function(){
            $obj.html('');
            $obj.append('<div class="transfer" id="transfer'+_element.id+'"></div>');
            //获取穿梭框
            var $t = $('#transfer'+_element.id);
            //init穿梭框dom
            $t.append('<div class="transferLeft"><ul></ul></div>');
            $t.append('<div class="transBtnBox"><a class="transferBtn trnasferRightAllBtn">>></a><a class="transferBtn trnasferRightBtn">></a><a class="transferBtn transferLeftBtn"><</a><a class="transferBtn trnasferLeftAllBtn"><<</a></div>');
            $t.append('<div class="transferRight"><ul></ul></div>');
            //定义穿梭框相关dom
            var transferLeft =$t.find('.transferLeft'),transferRight = $t.find('.transferRight'),$leftBtn = $t.find('.transferLeftBtn'),
            $rightBtn = $t.find('.trnasferRightBtn'),$leftallBtn = $t.find('.trnasferLeftAllBtn'),$rightallBtn = $t.find('.trnasferRightAllBtn');
            opts.data.left.length>0 ?
                opts.data.left.map(function(v,i){
                    $t.find('.transferLeft>ul').append('<li data-id="'+i+'"><input data-id="'+v.id+'" type="checkbox"/>'+v.value+'</li>');
            })
                :
                $t.find('.transferLeft>ul').append('<p style="margin-top: 40%;text-align: center;color: #c3c3c3;">无数据</p>');

            opts.data.right.length>0 ?
                opts.data.right.map(function(v,i){
                    $t.find('.transferRight>ul').append('<li data-id="'+i+'"><input data-id="'+v.id+'" type="checkbox"/>'+v.value+'</li>');
            })
                :
                $t.find('.transferRight>ul').append('<p style="margin-top: 40%;text-align: center;color: #c3c3c3;">无数据</p>');

            [$('.transferLeft>ul'),$('.transferRight>ul')].map(function(e,i){
              $(e).find('li').off().on('click',function (e) {
                  if(e.target.nodeName=='INPUT'){
                      return ;
                  }
                  var $check=$(this).find('input[type="checkbox"]');
                  $check.is(':checked')?$check[0].checked=false:$check[0].checked=true;
              })
            });

            //初始化搜索框
            if(opts.search){
                opts.search=='left'? this.setSearch($t.find('.transferLeft')):'';
                opts.search=='right'?this.setSearch($t.find('.transferRight')):'';
                opts.search=='all'?this.setSearch([$t.find('.transferLeft'),$t.find('.transferRight')]):'';
            }
            this.bindClick([$leftBtn,$leftallBtn,$rightBtn,$rightallBtn],[1,2,3,4],$t);
        }
        //绑定点击事件
        this.bindClick = function(arrayBtn,direction,parent){
            var t = this;
            arrayBtn.map(function(b,i){
                $(b).off().on('click',function(){
                    var isnull = false;
                   switch (direction[i]){
                       case 1:
                           var e = parent.find('.transferRight');
                           var _left = t.findChecked(e,false);
                           _left.length>0?
                           _left.map(function(v,i){
                               t.opts.data.right.map(function(a,k){
                                   if(a.id==v.id){
                                       t.opts.data.right.splice(k,1);
                                   }
                               })
                               t.opts.data.left.push(v);
                           }):isnull=true;
                           console.log(t.opts.data);
                           break;
                       case 2:
                           var e = parent.find('.transferRight');
                           var _left = t.findChecked(e,true);
                           _left.length>0?
                           _left.map(function (v) {
                               t.opts.data.right=[];
                               t.opts.data.left.push(v);
                           }):isnull=true;
                           break
                       case 3:
                           var e = parent.find('.transferLeft');
                           var _right = t.findChecked(e,false);
                           _right.length>0?
                           _right.map(function (v) {
                               t.opts.data.left.map(function(a,k){
                                   if(a.id==v.id){
                                       t.opts.data.left.splice(k,1);
                                   }
                               })
                               t.opts.data.right.push(v);
                           }):isnull=true;
                           break;
                       case 4:
                           var e = parent.find('.transferLeft');
                           var _right = t.findChecked(e,true);
                           _right.length>0?
                           _right.map(function (v) {
                               t.opts.data.left=[];
                               t.opts.data.right.push(v);
                           }):isnull=true;
                           break;
                   }
                   isnull?'':t.initElement();
                })
            })
        };
        //遍历选中的元素
        this.findChecked = function (e,all) {
            var checked=[];
            $(e).find('li').map(function (i,li) {
                var $input =   $(li).find('input[type="checkbox"]');
                all?
                checked.push({id:$input.attr('data-id'),value:$(li).text()}):$input.is(':checked')?checked.push({id:$input.attr('data-id'),value:$(li).text()}):''
            })
            return checked;
        }
        //设置搜索
        this.setSearch = function (element) {
            var t = this;
           element.map(function(e,i){
               $(e).prepend('<h4 class="transferTitle">'+opts.title[i]+'</h4><input class="'+$(e)[0].className+'Search" type="text" placeholder="搜索">');
               var searchTool = $('.'+$(e)[0].className+'Search');
               searchTool.on('keyup',function(){
                   $(e).find('.noResult').remove();
                   var t = this,isNull=true;
                   var $li = $(this).next().find('li');
                   if($(this).val().trim()==''){
                       $li.removeClass('hide');
                       return ;
                   }
                   $li.map(function (i,v) {
                       if( $(v).text().indexOf($(t).val())>-1){
                           $(v).removeClass('hide');
                           isNull=false;
                       }else{
                           $(v).addClass('hide');
                       }
                  })
                   isNull?$(this).next().append('<li class="noResult">无筛选结果</li>'):'';
               })
           })
        }
        //定义初始化
        this.init=function () {
            this.initElement();
        }
        //初始化
        this.init();
    }
    $.fn.transfer = function(parameter,callback){
        if(typeof parameter == 'function'){//重载
            callback = parameter;
            parameter = {};
        }else{
            parameter = parameter || {};
            callback = callback || function(){};
        }
        var options = $.extend({},defaults,parameter);
        var transfer = new Transfer(this, options);
        //返回 transfer 实例，以便于后续操作
        return transfer;
    }
})