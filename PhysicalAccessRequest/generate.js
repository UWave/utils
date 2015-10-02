#!/usr/bin/env nodejs
var hummus = require('hummus');

function generateAccessRequest(args, hours) {
  var pdfWriter = hummus.createWriterToModify('template.pdf', {modifiedFilePath:'output.pdf'});
  var pageModifier = new hummus.PDFPageModifier(pdfWriter, 0);

  var boxlocations = {
    name: [64, 592],
    idnumber: [345, 592],
    email: [64, 550],
    phone: [280, 550],
    advisor: [60, 390],
    quarter: [60, 350],
    hours: [345, 350]
  };

  for(var arg in args) {
    if(args.hasOwnProperty(arg) && boxlocations.hasOwnProperty(arg)) {
      pageModifier.startContext().getContext().writeText(args[arg], boxlocations[arg][0], boxlocations[arg][1],  {
          font: pdfWriter.getFontForFile('./fonts/Ubuntu-L.ttf'),
          size: 14,
          colorspace: 'gray',
          color: 0x00
        });
    }
  }

  pageModifier.endContext().writePage();

  pdfWriter.end();

}

generateAccessRequest({
  name: "Hasit",
  idnumber: 1111111,
  email: "finn@uwave.fm",
  phone: "(202) 456-1414",
  advisor: "Amoshaun Toft",
  quarter: "Autum 2015",
  hours: "8:00am to 10pm"
}, {
  hours: 24
});
