from build import build_tool_page, tools

PDF_ENGINE_HEAD = '<script src="/assets/js/pdf-engine.js"></script>'

def register():
    # ---------------- PDF to Word ----------------
    panel = """
    <div id="pw-dropzone" class="drop-zone">
      <span class="drop-zone-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4 4 0 0 1-1-7.9A5.5 5.5 0 0 1 16.9 8H17a4 4 0 0 1 1 7.9"/><path d="M12 12v8m0-8l-3 3m3-3l3 3"/></svg></span>
      <p><strong>Drop your PDF here</strong></p>
      <p class="drop-zone-sub">or</p>
      <label class="btn btn-secondary" for="pw-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="pw-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. Processed entirely in your browser.</p>
      <div class="drop-zone-trust"><span>Free</span><span>&middot;</span><span>Fast</span><span>&middot;</span><span>Secure</span></div>
    </div>
    <div class="notice">
      This tool extracts the <strong>text content</strong> of your PDF into an editable Word document.
      It works best for text-based PDFs (reports, essays, letters). Scanned/image-only PDFs have no
      extractable text, and complex layouts, tables and images are not preserved &mdash; only the text.
    </div>
    <div id="pw-options" style="display:none;margin-top:8px">
      <p class="field hint" id="pw-filename"></p>
      <div class="row-actions">
        <button type="button" id="pw-run" class="btn btn-primary">Convert to Word</button>
        <button type="button" id="pw-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="pw-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <p id="pw-result-text">Your Word document is ready.</p>
      <div class="row-actions"><a id="pw-download" class="btn btn-primary">Download .docx</a></div>
    </div>
    """
    script = """
    (function(){
      var file = null;
      var dz = document.getElementById('pw-dropzone');
      var input = document.getElementById('pw-file');
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('pw-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('pw-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        document.getElementById('pw-options').style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      document.getElementById('pw-run').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Converting...';
        try {
          setProgress('Loading PDF engine...');
          var pdfjsLib = await window.ToolNagriPDF.ensurePdfJs();
          var buf = await file.arrayBuffer();
          var pdf = await pdfjsLib.getDocument({ data: buf }).promise;
          var docxLib = await window.ToolNagriPDF.ensureDocx();
          var children = [];
          var hasAnyText = false;
          for (var i=1; i<=pdf.numPages; i++){
            setProgress('Extracting text from page ' + i + ' of ' + pdf.numPages + '...');
            var text = await window.ToolNagriPDF.extractPageText(pdf, i);
            children.push(new docxLib.Paragraph({ text: 'Page ' + i, heading: docxLib.HeadingLevel.HEADING_2 }));
            if (text.trim()) {
              hasAnyText = true;
              var lines = text.split(/\\s{2,}|\\n/).map(function(s){return s.trim();}).filter(Boolean);
              if (lines.length === 0) lines = [text];
              lines.forEach(function(line){
                children.push(new docxLib.Paragraph({ children: [new docxLib.TextRun(line)] }));
              });
            } else {
              children.push(new docxLib.Paragraph({ children: [new docxLib.TextRun({text:'(No extractable text on this page \u2014 it may be a scanned image.)', italics:true})] }));
            }
          }
          if (!hasAnyText) {
            throw new Error('no_text');
          }
          setProgress('Building Word document...');
          var doc = new docxLib.Document({ sections: [{ properties: {}, children: children }] });
          var blob = await docxLib.Packer.toBlob(doc);
          var baseName = file.name.replace(/\\.pdf$/i, '');
          document.getElementById('pw-download').href = URL.createObjectURL(blob);
          document.getElementById('pw-download').setAttribute('download', baseName + '.docx');
          document.getElementById('pw-result-text').textContent = 'Extracted text from ' + pdf.numPages + ' page(s) into an editable Word document.';
          setProgress(null);
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          if (err && err.message === 'no_text') {
            showError('No extractable text was found in this PDF \u2014 it looks like a scanned/image-only document, which this tool cannot convert to text.');
          } else {
            showError('The conversion engine failed to load or this file could not be processed. Please check your internet connection and try again.');
          }
        } finally {
          btn.disabled = false; btn.textContent = 'Convert to Word';
        }
      });

      document.getElementById('pw-reset').addEventListener('click', function(){
        file = null; input.value = '';
        document.getElementById('pw-options').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """
    build_tool_page(
        "pdf-to-word", panel, script,
        how_it_works="<p>Your PDF's text is extracted page-by-page using pdf.js's text layer (the same layer that lets you select text in a PDF viewer), then assembled into a real .docx Word document with one heading per page, using an open-source document-generation library. Only text is extracted &mdash; page layout, images, columns and tables are not reconstructed. Nothing is uploaded to a server.</p>",
        example="<p>Upload a 4-page text report and download a Word document with 4 sections (\"Page 1\" through \"Page 4\"), each containing that page's text as editable paragraphs.</p>",
        faqs=[
            ("Will my PDF's exact formatting (fonts, columns, images) be preserved?", "No. This tool extracts text content only, so you'll need to reformat the document in Word if you need to match the original's exact visual layout."),
            ("What if my PDF is a scanned document?", "Scanned PDFs are images, not text, so there's nothing to extract. This tool will tell you clearly if no text was found rather than producing an empty document."),
            ("Is this a real, editable Word file?", "Yes &mdash; it's a genuine .docx file you can open and edit in Microsoft Word, Google Docs, or LibreOffice, not an image or a PDF renamed."),
        ],
        disclaimer="This tool extracts text only; visual layout, tables and images are not preserved. For scanned/image-only PDFs, no text can be extracted.",
        related_override=[t for t in tools if t['slug'] in ('pdf-to-excel','pdf-to-ppt','split-pdf','compress-pdf')],
        extra_head=PDF_ENGINE_HEAD,
    )

    # ---------------- PDF to PPT ----------------
    panel = """
    <div id="pp-dropzone" class="drop-zone">
      <span class="drop-zone-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4 4 0 0 1-1-7.9A5.5 5.5 0 0 1 16.9 8H17a4 4 0 0 1 1 7.9"/><path d="M12 12v8m0-8l-3 3m3-3l3 3"/></svg></span>
      <p><strong>Drop your PDF here</strong></p>
      <p class="drop-zone-sub">or</p>
      <label class="btn btn-secondary" for="pp-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="pp-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. Processed entirely in your browser.</p>
      <div class="drop-zone-trust"><span>Free</span><span>&middot;</span><span>Fast</span><span>&middot;</span><span>Secure</span></div>
    </div>
    <div class="notice">
      Each PDF page becomes a <strong>full-slide image</strong> in the .pptx file. This preserves the exact
      visual appearance of every page (great for scanned decks or design-heavy PDFs), but text inside the
      slides will not be individually editable in PowerPoint.
    </div>
    <div id="pp-options" style="display:none;margin-top:8px">
      <p class="field hint" id="pp-filename"></p>
      <div class="row-actions">
        <button type="button" id="pp-run" class="btn btn-primary">Convert to PowerPoint</button>
        <button type="button" id="pp-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="pp-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <p id="pp-result-text">Your PowerPoint file is ready.</p>
      <div class="row-actions"><a id="pp-download" class="btn btn-primary">Download .pptx</a></div>
    </div>
    """
    script = """
    (function(){
      var file = null;
      var dz = document.getElementById('pp-dropzone');
      var input = document.getElementById('pp-file');
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('pp-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('pp-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        document.getElementById('pp-options').style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      document.getElementById('pp-run').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Converting...';
        try {
          setProgress('Loading PDF engine...');
          var pdfjsLib = await window.ToolNagriPDF.ensurePdfJs();
          var buf = await file.arrayBuffer();
          var pdf = await pdfjsLib.getDocument({ data: buf }).promise;
          var PptxGenJS = await window.ToolNagriPDF.ensurePptxGenJS();
          var pres = new PptxGenJS();
          pres.defineLayout({ name: 'PDFPAGE', width: 10, height: 7.5 });
          pres.layout = 'PDFPAGE';
          for (var i=1; i<=pdf.numPages; i++){
            setProgress('Rendering slide ' + i + ' of ' + pdf.numPages + '...');
            var canvas = await window.ToolNagriPDF.renderPageToCanvas(pdf, i, 1.8);
            var dataUrl = canvas.toDataURL('image/jpeg', 0.85);
            var slide = pres.addSlide();
            var aspect = canvas.width / canvas.height;
            var w = 10, h = 10/aspect;
            if (h > 7.5) { h = 7.5; w = 7.5*aspect; }
            slide.addImage({ data: dataUrl, x: (10-w)/2, y: (7.5-h)/2, w: w, h: h });
          }
          setProgress('Finalizing presentation...');
          var blob = await pres.write({ outputType: 'blob' });
          var baseName = file.name.replace(/\\.pdf$/i, '');
          document.getElementById('pp-download').href = URL.createObjectURL(blob);
          document.getElementById('pp-download').setAttribute('download', baseName + '.pptx');
          document.getElementById('pp-result-text').textContent = 'Created a ' + pdf.numPages + '-slide PowerPoint file.';
          setProgress(null);
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          showError('The conversion engine failed to load or this file could not be processed. Please check your internet connection and try again.');
        } finally {
          btn.disabled = false; btn.textContent = 'Convert to PowerPoint';
        }
      });

      document.getElementById('pp-reset').addEventListener('click', function(){
        file = null; input.value = '';
        document.getElementById('pp-options').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """
    build_tool_page(
        "pdf-to-ppt", panel, script,
        how_it_works="<p>Each page of your PDF is rendered to a high-resolution image using pdf.js, and each image becomes one full-slide picture in a new .pptx file, built with an open-source presentation-generation library. This preserves the exact look of every page. Nothing is uploaded to a server.</p>",
        example="<p>Upload a 12-page PDF deck and download a 12-slide .pptx where each slide shows that page exactly as it appeared in the PDF.</p>",
        faqs=[
            ("Can I edit the text on each slide afterwards?", "Not directly &mdash; each slide is a single image, so text within it isn't a separate, editable PowerPoint text box. This approach prioritizes preserving the exact visual design over editability."),
            ("Why use images instead of rebuilding real text/shapes?", "Reconstructing a PDF's original text boxes, fonts and positions as fully editable PowerPoint objects is extremely complex and unreliable to do for free. The image-per-slide approach is honest about that trade-off and guarantees the output looks right."),
        ],
        disclaimer="Each slide is a static image of the original page; text and objects are not individually editable in PowerPoint.",
        related_override=[t for t in tools if t['slug'] in ('pdf-to-word','pdf-to-excel','pdf-to-jpg','split-pdf')],
        extra_head=PDF_ENGINE_HEAD,
    )

    # ---------------- PDF to Excel ----------------
    panel = """
    <div id="px-dropzone" class="drop-zone">
      <span class="drop-zone-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4 4 0 0 1-1-7.9A5.5 5.5 0 0 1 16.9 8H17a4 4 0 0 1 1 7.9"/><path d="M12 12v8m0-8l-3 3m3-3l3 3"/></svg></span>
      <p><strong>Drop your PDF here</strong></p>
      <p class="drop-zone-sub">or</p>
      <label class="btn btn-secondary" for="px-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="px-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. Processed entirely in your browser.</p>
      <div class="drop-zone-trust"><span>Free</span><span>&middot;</span><span>Fast</span><span>&middot;</span><span>Secure</span></div>
    </div>
    <div class="notice">
      This tool extracts text using each item's position on the page and groups it into rows and columns
      &mdash; it works best for <strong>simple tables and structured lists</strong> (invoices, price lists,
      basic reports). Complex multi-column layouts or scanned PDFs may not extract cleanly. Always check
      the output before relying on it.
    </div>
    <div id="px-options" style="display:none;margin-top:8px">
      <p class="field hint" id="px-filename"></p>
      <div class="row-actions">
        <button type="button" id="px-run" class="btn btn-primary">Convert to Excel</button>
        <button type="button" id="px-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="px-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <p id="px-result-text">Your Excel file is ready.</p>
      <div class="row-actions"><a id="px-download" class="btn btn-primary">Download .xlsx</a></div>
    </div>
    """
    script = """
    (function(){
      var file = null;
      var dz = document.getElementById('px-dropzone');
      var input = document.getElementById('px-file');
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('px-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('px-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        document.getElementById('px-options').style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      document.getElementById('px-run').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Converting...';
        try {
          setProgress('Loading PDF engine...');
          var pdfjsLib = await window.ToolNagriPDF.ensurePdfJs();
          var buf = await file.arrayBuffer();
          var pdf = await pdfjsLib.getDocument({ data: buf }).promise;
          var xlsxHelper = await window.ToolNagriPDF.ensureXlsxHelper();
          var sheets = [];
          var hasAnyText = false;
          for (var i=1; i<=pdf.numPages; i++){
            setProgress('Extracting page ' + i + ' of ' + pdf.numPages + '...');
            var rows = await window.ToolNagriPDF.extractPageTable(pdf, i);
            if (rows.length) hasAnyText = true;
            sheets.push({ name: 'Page ' + i, rows: rows.length ? rows : [['(No extractable text on this page)']] });
          }
          if (!hasAnyText) throw new Error('no_text');
          setProgress('Building workbook...');
          var blob = await xlsxHelper.buildXlsxBlob(sheets);
          var baseName = file.name.replace(/\\.pdf$/i, '');
          document.getElementById('px-download').href = URL.createObjectURL(blob);
          document.getElementById('px-download').setAttribute('download', baseName + '.xlsx');
          document.getElementById('px-result-text').textContent = 'Extracted ' + pdf.numPages + ' page(s) into an Excel workbook (one sheet per page).';
          setProgress(null);
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          if (err && err.message === 'no_text') {
            showError('No extractable text was found in this PDF \u2014 it looks like a scanned/image-only document.');
          } else {
            showError('The conversion engine failed to load or this file could not be processed. Please check your internet connection and try again.');
          }
        } finally {
          btn.disabled = false; btn.textContent = 'Convert to Excel';
        }
      });

      document.getElementById('px-reset').addEventListener('click', function(){
        file = null; input.value = '';
        document.getElementById('px-options').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """
    build_tool_page(
        "pdf-to-excel", panel, script,
        how_it_works="<p>For each page, pdf.js reports the exact position of every piece of text. This tool groups text items that sit on roughly the same horizontal line into a row, and orders items within a row left-to-right into columns &mdash; a best-effort table reconstruction. The result is written into an .xlsx workbook (one sheet per PDF page) using an open-source spreadsheet library. Nothing is uploaded to a server.</p>",
        example="<p>Upload a 2-page PDF price list and download an Excel workbook with two sheets, each row corresponding to a line of the original table.</p>",
        faqs=[
            ("Will complex tables extract perfectly?", "Not always. Multi-column layouts, merged cells, or tables with irregular spacing may not line up perfectly into rows and columns. Always review the output before using it."),
            ("What happens with scanned PDFs?", "Scanned pages have no extractable text, so there's nothing to put into the spreadsheet. The tool will tell you clearly rather than producing an empty file."),
            ("Is each PDF page a separate sheet?", "Yes, to keep each page's rows from mixing together when column alignment differs between pages."),
        ],
        disclaimer="Table reconstruction is best-effort based on text position and works best for simple, well-aligned tables. Always verify extracted data before use.",
        related_override=[t for t in tools if t['slug'] in ('pdf-to-word','pdf-to-ppt','split-pdf','compress-pdf')],
        extra_head=PDF_ENGINE_HEAD,
    )
