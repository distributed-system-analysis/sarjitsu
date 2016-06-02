var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

if (system.args.length < 3 || system.args.length > 5) {
    console.log('Usage: rasterize.js URL filename [paperwidth*paperheight|paperformat] [zoom]');
    console.log('  paper (pdf output) examples: "5in*7.5in", "10cm*20cm", "A4", "Letter"');
    console.log('  image (png/jpg output) examples: "1920px" entire page, window width 1920px');
    console.log('                                   "800px*600px" window, clipped to 800x600');
    phantom.exit(1);
} else {
    address = system.args[1];
    output = system.args[2];
    page.viewportSize = { width: 600, height: 600 };
    page.evaluate(function() {
	var style = document.createElement('style'),
	text = document.createTextNode('body { background: #fff }');
	style.setAttribute('type', 'text/css');
	style.appendChild(text);
	document.head.insertBefore(style, document.head.firstChild);
    });

    if (system.args.length >= 3 && system.args[2].substr(-4) === ".pdf") {
        // size = system.args[3].split('*');
	// //page.paperSize = { height: '1024px', width: '1920px',  margin: '1cm' };
        // page.paperSize = size.length === 2 ? { width: size[0], height: size[1], margin: '0px' }
        // : { format: system.args[3], orientation: 'portrait', margin: '1cm' };	
	page.paperSize = {
	    format: 'A3',
	    orientation: 'landscape',
	    margin: '1cm'
	};
	page.viewportSize = { width: 1300, height: 1080 };	
    } 
    else {
	page.paperSize = {
	    format: 'A3',
	    orientation: 'landscape',
	    margin: '1cm'
	};
	page.viewportSize = { width: 1100, height: 1080 };
    }

    if (system.args.length > 4) {
        page.zoomFactor = system.args[4];
    }
    page.open(address, function (status) {
        if (status !== 'success') {
            console.log('Unable to load the address!');
            phantom.exit(1);
        } else {
            window.setTimeout(function () {
                page.render(output);
                phantom.exit();
            }, 2000);
        }
    });
}

function just_wait(output) {
    window.setTimeout(function() {
        page.render(output);
        phantom.exit();
    }, 2000);
}
