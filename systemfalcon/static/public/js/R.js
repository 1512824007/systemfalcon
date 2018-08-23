/**
 * Created by Liang on 2017/6/8.
 */

const monitor = {};

monitor.DashBoard = function(){

}
monitor.Device = function(){

}
monitor.MonitorInfo = function(){

}
monitor.ServerRoom = function(){

}
monitor.TroubleBI = function(){

}
monitor.TroubleList = function(){
    $('select').chosen({disable_search_threshold:10,max_selected_options: 5,no_results_text:'未搜索到结果'});
    $('.moreSearchBox').addClass('hide');
    $('.moreSearch').on('click',function () {
        if($('.moreSearchBox').hasClass('hide')){
            $('.moreSearchBox').removeClass('hide');
            $(this).find('i').removeClass('glyphicon-menu-down');
            $(this).find('i').addClass('glyphicon-menu-up');
        }else{
            $('.moreSearchBox').addClass('hide');
            $(this).find('i').removeClass('glyphicon-menu-up');
            $(this).find('i').addClass('glyphicon-menu-down');
        }
    });
    $('.TroubleTab').find('li').each(function(){
        $(this).off().on('click',function(){
            $('.TroubleTab').find('li').removeClass('active');
            $(this).addClass('active');
            $('.tabBox').addClass('hide');
            $(('.'+$(this).attr('data-id'))).removeClass('hide');
        })
    });
}
monitor.TroubleInfo = function(){

}
monitor.UserRequest = function(){

}
monitor.SignUp=function(){
    $('.nextBtn').on('click',function(){
        $('.SignBox').addClass('hide');
        $($('.SignBox')[$(this).attr('data-id')]).removeClass('hide');
    });
}
monitor.userManage=function () {
    $('.addUser').on('click',function(){
       var $modal = $('.addUserModal');
       var transfer1 = $('#transfer1').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部用户组','所属用户组']
        });
       var transfer2 = $('#transfer2').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部系统功能','可使用系统功能']
        });
       console.log(transfer1);
        $modal.modal('show');
        $modal.find('.nextBtn').off().on('click',function () {
            $modal.find('.formBox').addClass('hide');
            $modal.find('.transBox').removeClass('hide');
            $modal.find('.formBtnBox').addClass('hide');
            $modal.find('.tansBtnBox').removeClass('hide')
       });
        $modal.find('.preBtn').off().on('click',function () {
            $modal.find('.formBox').removeClass('hide');
            $modal.find('.transBox').addClass('hide');
            $modal.find('.formBtnBox').removeClass('hide');
            $modal.find('.tansBtnBox').addClass('hide')
        })
    });
    $('.importUser').on('click',function () {
        $('.importUserModal').modal('show');
        $('.fileImport').off().on('click',function () {
            $('#importFile').click();
        })
    })
    $('.deleteHandle').on('click',function () {
        $('.deleteModal').modal('show');
    })
    $('.resetBtn').on('click',function () {
        $('.resetPswModal').modal('show');
    });
    $('.manageBtn').on('click',function () {
        var $modal = $('.manageModal');
        var transfer1 = $('#transfer3').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部用户组','所属用户组']
        });
        var transfer2 = $('#transfer4').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部系统功能','可是哟那个系统功能']
        });
        console.log(transfer1);
        $modal.modal('show');
        $modal.find('.nextBtn').off().on('click',function () {
            $modal.find('.formBox').addClass('hide');
            $modal.find('.transBox').removeClass('hide');
            $modal.find('.formBtnBox').addClass('hide');
            $modal.find('.tansBtnBox').removeClass('hide')
        });
        $modal.find('.preBtn').off().on('click',function () {
            $modal.find('.formBox').removeClass('hide');
            $modal.find('.transBox').addClass('hide');
            $modal.find('.formBtnBox').removeClass('hide');
            $modal.find('.tansBtnBox').addClass('hide')
        })
    })
}
monitor.userInfo=function () {
    
}
monitor.userGroupManage=function () {
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
    $('.manageBtn').on('click',function () {
        var transfer1 = $('#transfer1').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部用户组','所属用户组']
        });
        var transfer2 = $('#transfer2').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部系统功能','可使用系统功能']
        });
        $('.manageGroupModal').modal('show');
    })
    $('.addGroupBtn').on('click',function () {
        var transfer3 = $('#transfer3').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部用户组','所属用户组']
        });
        var transfer4 = $('#transfer4').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部系统功能','可使用系统功能']
        });
        $('.addGroupModal').modal('show');
    })
}
monitor.configManage = function () {
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
    $('.manageBtn').on('click',function () {
        $('.manageGroupModal').modal('show');
    })
    $('.addConfigBtn').on('click',function () {
        $('.addGroupModal').modal('show');
    })
}
monitor.configGroupManage=function () {
    $('.addGroupBtn').on('click',function () {
        $('#transfer1').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数','包含参数']
        });
        $('#transfer2').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数组','包含参数组']
        });
        $('.addGroupModal').modal('show');
    })
    $('.ManageGroupBtn').on('click',function () {
        $('#transfer3').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数','包含参数']
        });
        $('#transfer4').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数组','包含参数组']
        });
        $('.manageGroupModal').modal('show');
    })
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.CollectorManage=function () {
    $('.addToolsBtn').on('click',function () {
        $('.addToolsModal').modal('show');
        $('#transfer2').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数','采集参数']
        });
    })
    $('.manageBtn').on('click',function () {
        $('.manageToolsModal').modal('show');
        $('#transfer1').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部参数','采集参数']
        });
    })
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.AlarmModeConfig=function () {
    $('.addAlarmMode').on('click',function () {
        $('.addAlarmModal').modal('show');
    });
    $('.ManageAlarmBtn').on('click',function () {
        $('.manageAlarmModal').modal('show');
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.AlarmFormat=function () {
    $('.addAlarmMode').on('click',function () {
        $('.addAlarmModal').modal('show');
    });
    $('.ManageAlarmBtn').on('click',function () {
        $('.manageAlarmModal').modal('show');
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.SystemMaintenanceManage=function () {
    $('.addMaintenanceManage').on('click',function () {
        $('.addMaintenanceModal').modal('show');
    })
    $('.manageBtn').on('click',function () {
        $('.manageMaintenanceModal').modal('show');
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.TroubleThresholdConfig=function () {
    $('.addThresholdConfig').on('click',function () {
        $('.addThresholdModal').modal('show');
    });

    $('.manageBtn').on('click',function () {
        $('.manageThresholdModal').modal('show');
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.TroubleDefineManage=function () {
    $('.addTroubleDefine').on('click',function () {
        $('.addTroubleDefineModal').modal('show');
    })
    $('.manageBtn').on('click',function () {
        $('.manageTroubleDefineModal').modal('show');
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.DeviceMonitorConfig = function () {
    $('.addMonitorBtn').on('click',function () {
        $('.addMonitorModal').modal('show');
        $('.nextBtn').on('click',function () {
            $(this).closest('.modal').find('.one').addClass('hide');
            $(this).closest('.modal').find('.two').removeClass('hide');
        })
        $('.preBtn').on('click',function () {
            $(this).closest('.modal').find('.two').addClass('hide');
            $(this).closest('.modal').find('.one').removeClass('hide');
        })
    })
    $('.manageBtn').on('click',function () {
        $('.manageMonitorModal').modal('show');
        $('.nextBtn').on('click',function () {
            $(this).closest('.modal').find('.one').addClass('hide');
            $(this).closest('.modal').find('.two').removeClass('hide');
        })
        $('.preBtn').on('click',function () {
            $(this).closest('.modal').find('.two').addClass('hide');
            $(this).closest('.modal').find('.one').removeClass('hide');
        })
    });
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
}
monitor.DeviceMonitorManage=function () {
    $('.addDevice').on('click',function () {
        $('.addDeviceModal').modal('show');
        $('#transfer3').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部设备组','添加设备组']
        });
        $('#transfer4').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部设备','添加设备']
        });
    })
    $('.manageBtn').on('click',function () {
        $('.manageDeviceModal').modal('show');
        $('#transfer1').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部设备组','添加设备组']
        });
        $('#transfer2').transfer({
            search:'all',
            data:{
                left:[{id:1,value:1},{id:2,value:2},{id:3,value:3},{id:4,value:4},{id:5,value:5}],
                right:[{id:6,value:'ipipipip'},{id:7,value:'asdf'}]
            },
            title:['全部设备','添加设备']
        });
    })
    $('.deleteBtn').on('click',function () {
        $('.deleteModal').modal('show');
    })
    $('.deviceListBtn').on('click',function () {
        $('.deviceListModal').modal('show');
    })
}