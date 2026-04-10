window.WP_Grid_Builder&&WP_Grid_Builder.on('init',function(wpgb){wpgb.facets.on('appended',function(content){content.forEach((container,index)=>{if(typeof doExtrasAccordion=='function'){doExtrasAccordion(container)
if(((content.length-1)===index)&&container.closest('.x-accordion.wpgb-enabled')){if(container.parentNode&&container.parentNode.parentNode){doExtrasAccordion(container.parentNode.parentNode)}}}
if(typeof doExtrasSlider=='function'){doExtrasSlider(container)}
if(typeof doExtrasReadmore=='function'){setTimeout(()=>{doExtrasReadmore(container)},100)}
if(typeof doExtrasLightbox=='function'){if(container.parentElement){container.parentElement.querySelectorAll('.brxe-xdynamiclightbox').forEach(otherLightbox=>{if(undefined!==window.xDynamicLightbox.Instances[otherLightbox.dataset.xId]){window.xDynamicLightbox.Instances[otherLightbox.dataset.xId].destroy()}})
if((content.length-1)===index){setTimeout(()=>{doExtrasLightbox(container.parentElement,!0)},1000)}}}
if(typeof doExtrasSocialShare=='function'){doExtrasSocialShare(container)}
if(typeof doExtrasOffCanvas=='function'){doExtrasOffCanvas(container)}
if(typeof doExtrasModal=='function'){doExtrasModal(container)}
if(typeof doExtrasPopover=='function'){doExtrasPopover(container)}
if(typeof doExtrasTimeline=='function'){window.dispatchEvent(new Event('resize'))}
if(typeof doExtrasTabs=='function'){doExtrasTabs(container)}
if(typeof doExtrasLottie=='function'){doExtrasLottie(container,!0)}
if(typeof doExtrasMediaPlayer=='function'){doExtrasMediaPlayer(container)}
if(typeof doExtrasCopyToClipBoard=='function'){doExtrasCopyToClipBoard(container)}
if(typeof doExtrasCopyToClipBoardPopover=='function'){doExtrasCopyToClipBoardPopover(container)}
if(typeof doExtrasDynamicMap=='function'){if(container.closest('.brxe-section')){doExtrasDynamicMap(container.closest('.brxe-section'))}}
if(typeof doExtrasParallax=='function'){doExtrasParallax(container)}
if(typeof doExtrasTilt=='function'){doExtrasTilt(container)}
if(typeof doExtrasInteractions=='function'){doExtrasInteractions(container)}
if(typeof doExtrasTable=='function'){doExtrasTable(container)}
if(typeof doExtrasChart=='function'){doExtrasChart(container)}
if(typeof doExtrasBeforeAfterImage=='function'){doExtrasBeforeAfterImage(container)}
if(typeof doExtrasCountdown=='function'){doExtrasCountdown(container)}
if(typeof doExtrasImageHotspots=='function'){doExtrasImageHotspots(container)}
if(typeof doExtrasToggleSwitch=='function'){doExtrasToggleSwitch(container)}
if(typeof doExtrasFavorite=='function'){doExtrasFavorite(container)
if(typeof doExtrasFavoritePopover=='function'){doExtrasFavoritePopover(container)}}})})})