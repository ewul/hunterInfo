$.extend($.fn.datagrid.defaults.editors, {
	datebox: {
		init: function(container, options){
			var input=$('<input class="easyui-datebox">').appendTo(container);
			return input.datebox({
				format:function(date){
					return new Date(date).format("M/d/yyyy");
				}
			});
		},
		getValue: function(target){
			return $(target).parent().find('input.textbox-value').val();
		},
		
		setValue: function(target, value){
			$(target).datebox('setValue',value);
		},
		
		resize: function(target, width){
			var input=$(target);
			if($.boxModel == true){
				input.width(width - (input.outerWidth() - input.width()));
			}else{
				input.width(width);
			}
		}
		
	}
});
