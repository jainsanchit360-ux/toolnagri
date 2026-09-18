from build import build_tool_page, tools

PDF_ENGINE_HEAD = '<script src="/assets/js/pdf-engine.js"></script>'
PDF_LIB_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>'

def register():
    # ---------------- Split PDF ----------------
    panel = """
    <div id="sp-dropzone" class="drop-zone">
      <p><strong>Drag & drop a PDF here</strong>, or</p>
      <label class="btn btn-secondary" for="sp-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="sp-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. Processed entirely in your browser.</p>
    </div>
    <div id="sp-options" style="display:none;margin-top:16px">
      <p class="field hint" id="sp-filename"></p>
      <div class="field">
        <label for="sp-mode">Split mode</label>
        <select id="sp-mode">
          <option value="all">Every page as a separate PDF</option>
          <option value="range">Extract a custom page range</option>
        </select>
      </div>
      <div id="sp-range-field" class="field" style="display:none">
        <label for="sp-range">Page range (e.g. 1-3 or 1,3,5)</label>
        <input id="sp-range" type="text" placeholder="1-3">
      </div>
      <div class="row-actions">
        <button type="button" id="sp-run" class="btn btn-primary">Split PDF</button>
        <button type="button" id="sp-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="sp-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <p id="sp-result-text">Your split PDF is ready.</p>
      <div class="row-actions"><a id="sp-download" class="btn btn-primary">Download</a></div>
    </div>
    """
    script = """
    (function(){
      var file = null;
      var dz = document.getElementById('sp-dropzone');
      var input = document.getElementById('sp-file');
      var modeSel = document.getElementById('sp-mode');
      modeSel.addEventListener('change', function(){
        document.getElementById('sp-range-field').style.display = modeSel.value === 'range' ? 'block' : 'none';
      });
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('sp-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('sp-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        document.getElementById('sp-options').style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      function parseRange(str, maxPage){
        var pages = new Set();
        var parts = str.split(',');
        for (var i=0;i<parts.length;i++){
          var p = parts[i].trim();
          if (!p) continue;
          if (p.indexOf('-') > -1) {
            var bounds = p.split('-').map(function(n){ return parseInt(n.trim(),10); });
            if (bounds.length !== 2 || isNaN(bounds[0]) || isNaN(bounds[1])) throw new Error('bad_range');
            for (var n=bounds[0]; n<=bounds[1]; n++) pages.add(n);
          } else {
            var num = parseInt(p,10);
            if (isNaN(num)) throw new Error('bad_range');
            pages.add(num);
          }
        }
        var arr = Array.from(pages).sort(function(a,b){return a-b;});
        if (arr.length === 0) throw new Error('bad_range');
        if (arr[0] < 1 || arr[arr.length-1] > maxPage) throw new Error('out_of_range');
        return arr;
      }

      function friendlyError(msg){ var e = new Error(msg); e.isFriendly = true; return e; }

      document.getElementById('sp-run').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        if (typeof PDFLib === 'undefined') { showError('The PDF library failed to load. Please check your internet connection and try again.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Splitting...';
        try {
          setProgress('Reading PDF...');
          var bytes = await file.arrayBuffer();
          var src;
          try {
            src = await PDFLib.PDFDocument.load(bytes, {ignoreEncryption:true});
          } catch (loadErr) {
            throw friendlyError('This file could not be read as a PDF. It may be corrupted, password-protected, or not a valid PDF file.');
          }
          var pageCount = src.getPageCount();
          var baseName = file.name.replace(/\\.pdf$/i, '');

          if (modeSel.value === 'range') {
            var rangeStr = document.getElementById('sp-range').value.trim();
            if (!rangeStr) { throw friendlyError('Please enter a page range, like "1-3" or "1,3,5".'); }
            var pages;
            try { pages = parseRange(rangeStr, pageCount); }
            catch (e) {
              if (e.message === 'out_of_range') throw friendlyError('This PDF only has ' + pageCount + ' pages. Please enter a range within 1-' + pageCount + '.');
              throw friendlyError('Please enter a valid page range, like "1-3" or "1,3,5".');
            }
            setProgress('Extracting ' + pages.length + ' page(s)...');
            var outDoc = await PDFLib.PDFDocument.create();
            var copied = await outDoc.copyPages(src, pages.map(function(p){ return p-1; }));
            copied.forEach(function(p){ outDoc.addPage(p); });
            var outBytes = await outDoc.save();
            var blob = new Blob([outBytes], {type:'application/pdf'});
            document.getElementById('sp-download').href = URL.createObjectURL(blob);
            document.getElementById('sp-download').setAttribute('download', baseName + '-pages-' + rangeStr.replace(/[^0-9,\\-]/g,'') + '.pdf');
            document.getElementById('sp-result-text').textContent = 'Extracted ' + pages.length + ' page(s) from your PDF.';
          } else {
            if (pageCount === 1) { throw friendlyError('This PDF only has 1 page, so there is nothing to split. Try a multi-page PDF.'); }
            setProgress('Splitting into ' + pageCount + ' individual PDFs...');
            var JSZip = await window.ToolNagriPDF.ensureJSZip();
            var zip = new JSZip();
            for (var i=0; i<pageCount; i++){
              setProgress('Processing page ' + (i+1) + ' of ' + pageCount + '...');
              var doc = await PDFLib.PDFDocument.create();
              var cp = await doc.copyPages(src, [i]);
              doc.addPage(cp[0]);
              var pBytes = await doc.save();
              zip.file(baseName + '-page-' + (i+1) + '.pdf', pBytes);
            }
            setProgress('Packaging into a zip...');
            var zipBlob = await zip.generateAsync({type:'blob'});
            document.getElementById('sp-download').href = URL.createObjectURL(zipBlob);
            document.getElementById('sp-download').setAttribute('download', baseName + '-split-pages.zip');
            document.getElementById('sp-result-text').textContent = 'Split into ' + pageCount + ' individual PDFs, packaged as a zip.';
          }
          setProgress(null);
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          showError(err && err.isFriendly ? err.message : 'Something went wrong reading or splitting this PDF. Please check the file and try again.');
        } finally {
          btn.disabled = false; btn.textContent = 'Split PDF';
        }
      });

      document.getElementById('sp-reset').addEventListener('click', function(){
        file = null; input.value = '';
        document.getElementById('sp-options').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """
    build_tool_page(
        "split-pdf", panel, script,
        how_it_works="<p>Your PDF is read directly in the browser using an open-source PDF library. In 'every page separate' mode, each page is copied into its own new PDF and all of them are packaged into a zip. In 'custom range' mode, only the pages you specify are copied into a single new PDF. The original file is never uploaded anywhere.</p>",
        example="<p>Upload a 10-page report and choose 'custom range' with \"1-3\" to get a 3-page PDF containing just the first section. Or choose 'every page separate' to get a zip with 10 single-page PDFs.</p>",
        faqs=[
            ("Can I extract non-consecutive pages?", "Yes. Use comma-separated values and ranges together, e.g. \"1,3,5-7\" extracts pages 1, 3, 5, 6 and 7 into one PDF."),
            ("Does splitting reduce quality?", "No. Pages are copied at their original quality; nothing is re-rendered or recompressed."),
            ("Is there a page limit?", "No hard limit, but very large PDFs (hundreds of pages) split into individual files may take a little longer and use more memory."),
        ],
        related_override=[t for t in tools if t['slug'] in ('merge-pdf','compress-pdf','pdf-to-jpg','jpg-to-pdf')],
        extra_head=PDF_ENGINE_HEAD + PDF_LIB_CDN,
    )

    # ---------------- Compress PDF ----------------
    panel = """
    <div id="cp-dropzone" class="drop-zone">
      <p><strong>Drag & drop a PDF here</strong>, or</p>
      <label class="btn btn-secondary" for="cp-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="cp-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. Processed entirely in your browser.</p>
    </div>
    <div class="notice">
      This tool re-encodes each page as an optimized image at the quality you choose. It works best for
      <strong>scanned documents and photo-heavy PDFs</strong>. For PDFs that are mostly typed text, compression
      gains may be small and the output text will no longer be selectable/searchable &mdash; for those files,
      consider keeping the original.
    </div>
    <div id="cp-options" style="display:none;margin-top:8px">
      <p class="field hint" id="cp-filename"></p>
      <div class="field">
        <label for="cp-quality">Compression level</label>
        <select id="cp-quality">
          <option value="0.4">High compression (smallest file, lower image quality)</option>
          <option value="0.65" selected>Balanced (recommended)</option>
          <option value="0.85">Low compression (larger file, best quality)</option>
        </select>
      </div>
      <div class="row-actions">
        <button type="button" id="cp-run" class="btn btn-primary">Compress PDF</button>
        <button type="button" id="cp-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="cp-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="result-grid">
        <div class="item"><div class="label">Original size</div><div class="val" id="cp-orig-size">-</div></div>
        <div class="item"><div class="label">New size</div><div class="val" id="cp-new-size">-</div></div>
        <div class="item"><div class="label">Change</div><div class="val" id="cp-change">-</div></div>
      </div>
      <div class="row-actions" style="margin-top:14px"><a id="cp-download" class="btn btn-primary">Download compressed PDF</a></div>
    </div>
    """
    script = """
    (function(){
      var file = null;
      var dz = document.getElementById('cp-dropzone');
      var input = document.getElementById('cp-file');
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('cp-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('cp-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        document.getElementById('cp-options').style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      document.getElementById('cp-run').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Compressing...';
        try {
          setProgress('Loading PDF engine...');
          var pdfjsLib = await window.ToolNagriPDF.ensurePdfJs();
          var PDFLibMod = await window.ToolNagriPDF.ensurePdfLib();
          var origBytes = await file.arrayBuffer();
          var pdf = await pdfjsLib.getDocument({ data: origBytes.slice(0) }).promise;
          var quality = parseFloat(document.getElementById('cp-quality').value);
          var outDoc = await PDFLibMod.PDFDocument.create();
          for (var i=1; i<=pdf.numPages; i++){
            setProgress('Compressing page ' + i + ' of ' + pdf.numPages + '...');
            var canvas = await window.ToolNagriPDF.renderPageToCanvas(pdf, i, 1.5);
            var jpgUrl = canvas.toDataURL('image/jpeg', quality);
            var jpgBytes = await (await fetch(jpgUrl)).arrayBuffer();
            var img = await outDoc.embedJpg(jpgBytes);
            var pageDims = img.scaleToFit(canvas.width, canvas.height);
            var page = outDoc.addPage([canvas.width, canvas.height]);
            page.drawImage(img, {x:0, y:0, width: canvas.width, height: canvas.height});
          }
          setProgress('Finalizing...');
          var outBytes = await outDoc.save();
          var origSize = origBytes.byteLength;
          var newSize = outBytes.byteLength;
          document.getElementById('cp-orig-size').textContent = window.ToolNagriPDF.formatBytes(origSize);
          document.getElementById('cp-new-size').textContent = window.ToolNagriPDF.formatBytes(newSize);
          var change = ((newSize - origSize) / origSize) * 100;
          document.getElementById('cp-change').textContent = (change <= 0 ? '' : '+') + change.toFixed(0) + '%';
          var blob = new Blob([outBytes], {type:'application/pdf'});
          var baseName = file.name.replace(/\\.pdf$/i, '');
          document.getElementById('cp-download').href = URL.createObjectURL(blob);
          document.getElementById('cp-download').setAttribute('download', baseName + '-compressed.pdf');
          setProgress(null);
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          showError('The PDF/compression engine failed to load or this file could not be processed. Please check your internet connection and try again.');
        } finally {
          btn.disabled = false; btn.textContent = 'Compress PDF';
        }
      });

      document.getElementById('cp-reset').addEventListener('click', function(){
        file = null; input.value = '';
        document.getElementById('cp-options').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """
    build_tool_page(
        "compress-pdf", panel, script,
        how_it_works="<p>Each page is rendered to an in-memory canvas using pdf.js, re-encoded as a JPEG at your chosen quality, and reassembled into a new PDF using an open-source PDF library. This is most effective for scanned documents and photo-heavy PDFs, where the original pages are already images. Nothing is uploaded &mdash; the whole process runs in your browser.</p>",
        example="<p>A 20-page scanned PDF at 8 MB, compressed at the 'Balanced' setting, often shrinks to 2-4 MB with only a modest, hard-to-notice drop in image sharpness.</p>",
        faqs=[
            ("Why did my file get bigger, not smaller?", "If your PDF is mostly typed text (not scanned images), rasterizing each page into a JPEG can sometimes produce a larger file than the original, highly efficient text encoding &mdash; and you'll lose selectable text in the process. This tool shows you the before/after size so you can decide whether to keep the compressed version."),
            ("Will the text still be selectable/searchable after compressing?", "No. Compression works by turning each page into an image, so the output PDF's pages are pictures of the original pages, not searchable text."),
            ("Is this a 'lossless' or 'lossy' compression?", "It's lossy &mdash; image quality is traded for file size, similar to how JPEG compression works for photos."),
        ],
        disclaimer="This tool trades image quality for file size and is not guaranteed to shrink every PDF — see 'Why did my file get bigger' in the FAQ below.",
        related_override=[t for t in tools if t['slug'] in ('split-pdf','merge-pdf','pdf-to-jpg','image-compressor')],
        extra_head=PDF_ENGINE_HEAD,
    )
