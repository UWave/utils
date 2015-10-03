#!/usr/bin/env nodejs
var hummus = require('hummus');

function generateAccessRequest(pageModifier, args, hours) {

  var boxlocations = {
    name: [64, 592],
    idnumber: [345, 592],
    email: [64, 550],
    phone: [280, 550],
    advisor: [60, 390],
    quarter: [60, 350],
    hours: [345, 350]
  };

  var ctx = pageModifier.startContext().getContext();

  for(var arg in args) {
    if(args.hasOwnProperty(arg) && boxlocations.hasOwnProperty(arg)) {
      ctx.writeText(args[arg], boxlocations[arg][0], boxlocations[arg][1],  {
          font: pdfWriter.getFontForFile('./fonts/Ubuntu-L.ttf'),
          size: 14,
          colorspace: 'gray',
          color: 0x00
        });
    }
  }

  switch(hours) {
    case 0:
      ctx.drawCircle(409, 415, 4, {type: "fill"});
      break;
    case 1:
      ctx.drawCircle(409, 401, 4, {type: "fill"});
      break;
    case 2:
      ctx.drawCircle(409, 387, 4, {type: "fill"});
      break;
  }

  ctx.drawCircle(164, 273, 4, {type: "fill"});
  ctx.drawCircle(164, 301, 4, {type: "fill"});

}

var pdfWriter = hummus.createWriterToModify('template.pdf', {modifiedFilePath:'output.pdf'});
var pageModifier = new hummus.PDFPageModifier(pdfWriter, 0);

generateAccessRequest({
  name: "Hasit",
  idnumber: 1111111,
  email: "finn@uwave.fm",
  phone: "(202) 456-1414",
  advisor: "Amoshaun Toft",
  quarter: "Autum 2015"
}, 0);

pageModifier.endContext().writePage();

pdfWriter.end();
