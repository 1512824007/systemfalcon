/**
 * Created by Liang on 2017/6/9.
 */
$(function(){
    $(document).on('scroll',function () {
        if($(document).scrollTop()==0){
            $('.backTop').css('display','none');
        }else{
            $('.backTop').css('display','block');
        }
    });
    $('.backTop').on('click',function () {
        window.scroll(0,0);
    });
    $('select').chosen({
        disable_search_threshold:10,
        allow_single_deselect : true,
        search_contains: true,
        max_selected_options: 5,
        no_results_text:'未搜索到结果',
        placeholder_text_multiple:'请选择'});
    $('.backMonitor').on('click',function(){
        window.location.href = '/monitor/MonitorInfo/';
    });
    $('.backUrlClick').on('click',function () {
        window.location.href = localStorage.backUrl;
    })
    $('.UrlStorageClick').off().on('click',function () {
        localStorage.backUrl = window.location.href;
        window.location.href = $(this).attr('data-url');
    })
    $('.innerToggle').on('click',function () {
        if($('.innerTab').hasClass('hide')){
            $('.innerTab').removeClass('hide');
            $(this).find('i').removeClass('glyphicon-menu-up');
            $(this).find('i').addClass('glyphicon-menu-down');
        }else{
            $('.innerTab').addClass('hide');
            $(this).find('i').removeClass('glyphicon-menu-down');
            $(this).find('i').addClass('glyphicon-menu-up');
        }
    })
})
