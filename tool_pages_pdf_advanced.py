from build import build_tool_page, tools

PDF_ENGINE_HEAD = '<script src="/assets/js/pdf-engine.js"></script>'

def _panel(accept_note, format_label):
    return """
    <div id="p2i-dropzone" class="drop-zone">
      <p><strong>Drag & drop a PDF here</strong>, or</p>
      <label class="btn btn-secondary" for="p2i-file" style="display:inline-flex;margin-top:6px">Choose PDF</label>
      <input id="p2i-file" type="file" accept="application/pdf" style="display:none">
      <p class="search-hint">One PDF at a time, up to 40 MB. """ + accept_note + """ Processed entirely in your browser.</p>
    </div>
    <div id="p2i-options" style="display:none;margin-top:16px">
      <p class="field hint" id="p2i-filename"></p>
      <div class="field">
        <label for="p2i-quality">Image quality: <span id="p2i-quality-val">85</span>%</label>
        <input id="p2i-quality" type="range" min="40" max="100" value="85">
      </div>
      <div class="row-actions">
        <button type="button" id="p2i-convert" class="btn btn-primary">Convert to """ + format_label + """</button>
        <button type="button" id="p2i-reset" class="btn btn-secondary">Choose another file</button>
      </div>
      <div id="p2i-progress" class="notice hidden"></div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <p id="p2i-result-text">Your images are ready.</p>
      <div class="row-actions"><a id="p2i-download" class="btn btn-primary">Download</a></div>
    </div>
    """

def _script(image_type, ext):
    return """
    (function(){
      var file = null;
      var dz = document.getElementById('p2i-dropzone');
      var input = document.getElementById('p2i-file');
      var optionsBox = document.getElementById('p2i-options');
      function showError(msg){
        var box = document.getElementById('error-box');
        box.textContent = msg; box.classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      function setProgress(msg){
        var p = document.getElementById('p2i-progress');
        if (!msg) { p.classList.add('hidden'); return; }
        p.textContent = msg; p.classList.remove('hidden');
      }
      function handleFile(f){
        document.getElementById('error-box').classList.add('hidden');
        if (f.type !== 'application/pdf') { showError('Please choose a PDF file.'); return; }
        if (f.size > 40*1024*1024) { showError('File is too large. Please choose a PDF under 40 MB.'); return; }
        file = f;
        document.getElementById('p2i-filename').textContent = 'Selected: ' + f.name + ' (' + window.ToolNagriPDF.formatBytes(f.size) + ')';
        optionsBox.style.display = 'block';
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
      input.addEventListener('change', function(){ if (input.files.length) handleFile(input.files[0]); input.value=''; });

      document.getElementById('p2i-quality').addEventListener('input', function(){
        document.getElementById('p2i-quality-val').textContent = this.value;
      });

      document.getElementById('p2i-convert').addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (!file) { showError('Please choose a PDF first.'); return; }
        var btn = this; btn.disabled = true; btn.textContent = 'Converting...';
        try {
          setProgress('Loading PDF engine...');
          var pdfjsLib = await window.ToolNagriPDF.ensurePdfJs();
          var buf = await file.arrayBuffer();
          var pdf = await pdfjsLib.getDocument({ data: buf }).promise;
          var quality = parseInt(document.getElementById('p2i-quality').value, 10) / 100;
          var baseName = file.name.replace(/\\.pdf$/i, '');
          var images = [];
          for (var i = 1; i <= pdf.numPages; i++) {
            setProgress('Rendering page ' + i + ' of ' + pdf.numPages + '...');
            var canvas = await window.ToolNagriPDF.renderPageToCanvas(pdf, i, 2);
            var dataUrl = canvas.toDataURL('""" + image_type + """', quality);
            images.push({ name: baseName + '-page-' + i + '.""" + ext + """', dataUrl: dataUrl });
          }
          if (images.length === 1) {
            setProgress(null);
            var res = await fetch(images[0].dataUrl);
            var blob = await res.blob();
            document.getElementById('p2i-download').href = URL.createObjectURL(blob);
            document.getElementById('p2i-download').setAttribute('download', images[0].name);
            document.getElementById('p2i-result-text').textContent = 'Your image is ready (1 page).';
          } else {
            setProgress('Packaging ' + images.length + ' images into a zip...');
            var JSZip = await window.ToolNagriPDF.ensureJSZip();
            var zip = new JSZip();
            for (var j = 0; j < images.length; j++) {
              var r = await fetch(images[j].dataUrl);
              var b = await r.blob();
              zip.file(images[j].name, b);
            }
            var zipBlob = await zip.generateAsync({ type: 'blob' });
            document.getElementById('p2i-download').href = URL.createObjectURL(zipBlob);
            document.getElementById('p2i-download').setAttribute('download', baseName + '-""" + ext + """-pages.zip');
            document.getElementById('p2i-result-text').textContent = 'Your images are ready (' + images.length + ' pages, packaged as a zip).';
            setProgress(null);
          }
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          setProgress(null);
          showError('The PDF engine failed to load or this file could not be processed. Please check your internet connection and try again, or try a different PDF.');
        } finally {
          btn.disabled = false; btn.textContent = 'Convert to """ + ('JPG' if ext=='jpg' else 'PNG') + """';
        }
      });

      document.getElementById('p2i-reset').addEventListener('click', function(){
        file = null; input.value = '';
        optionsBox.style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        setProgress(null);
      });
    })();
    """

def register():
    build_tool_page(
        "pdf-to-jpg",
        _panel("Every page becomes one JPG image.", "JPG"),
        _script("image/jpeg", "jpg"),
        how_it_works="<p>Each page of your PDF is rendered onto an in-memory canvas at high resolution using an open-source PDF rendering engine (pdf.js), then exported as a JPG at the quality level you choose. If your PDF has more than one page, all the JPGs are packaged into a single zip file for download. The file never leaves your device.</p>",
        example="<p>Upload a 5-page PDF, click convert, and download a zip containing page-1.jpg through page-5.jpg, each a full-resolution image of that page.</p>",
        faqs=[
            ("Does this upload my PDF anywhere?", "No. Rendering happens entirely in your browser using pdf.js. Your file is never sent to a server."),
            ("What quality should I choose?", "85% is a good default for sharing or archiving. Use 100% for print-quality output, or 40-60% for smaller files when sharing scanned text pages."),
            ("Can I convert just one page?", "Currently every page is converted. To get a single page, split the PDF first with the Split PDF tool, then convert the single-page result here."),
        ],
        related_override=[t for t in tools if t['slug'] in ('pdf-to-png','compress-pdf','split-pdf','jpg-to-pdf')],
        extra_head=PDF_ENGINE_HEAD,
    )

    build_tool_page(
        "pdf-to-png",
        _panel("Every page becomes one PNG image (supports transparency for pages with no background fill).", "PNG"),
        _script("image/png", "png"),
        how_it_works="<p>Each page of your PDF is rendered onto an in-memory canvas at high resolution using pdf.js, then exported as a PNG. PNG is lossless, so it's a good choice when you need crisp text or line art rather than the smaller file size of JPG. If your PDF has more than one page, all the PNGs are packaged into a single zip file. The file never leaves your device.</p>",
        example="<p>Upload a 3-page PDF slide deck, click convert, and download a zip with three full-resolution PNG images, one per slide.</p>",
        faqs=[
            ("PNG or JPG — which should I use?", "Use PNG for text, diagrams, or anything needing sharp edges. Use JPG (the PDF to JPG tool) for photos or when you want a smaller file size."),
            ("Does this upload my PDF anywhere?", "No. Rendering happens entirely in your browser. Your file is never sent to a server."),
        ],
        related_override=[t for t in tools if t['slug'] in ('pdf-to-jpg','compress-pdf','split-pdf','jpg-to-pdf')],
        extra_head=PDF_ENGINE_HEAD,
    )
