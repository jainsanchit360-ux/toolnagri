from build import build_tool_page, tools

PDF_LIB_SCRIPT = '<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>'

def register():
    # ---------------- JPG to PDF (with reorder, rotate, page-fit options) ----------------
    panel = """
    <div id="j2p-dropzone" class="drop-zone">
      <p><strong>Drag & drop images here</strong>, or</p>
      <label class="btn btn-secondary" for="j2p-file" style="display:inline-flex;margin-top:6px">Choose images</label>
      <input id="j2p-file" type="file" accept="image/jpeg,image/png" multiple style="display:none">
      <p class="search-hint">JPG or PNG, multiple files allowed, up to 15 MB each. Processed entirely in your browser.</p>
    </div>
    <ul id="j2p-list" class="file-list"></ul>
    <div id="j2p-pagesize-wrap" class="field" style="display:none;margin-top:10px">
      <label for="j2p-pagesize">Page size</label>
      <select id="j2p-pagesize">
        <option value="original">Fit page to each image (original size)</option>
        <option value="a4">Standard A4, image centered</option>
      </select>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    <div class="row-actions" style="margin-top:14px">
      <button type="button" id="j2p-generate" class="btn btn-primary" disabled>Convert to PDF</button>
      <button type="button" id="j2p-reset" class="btn btn-secondary">Clear all</button>
    </div>
    <div id="result-box" class="result-card hidden">
      <p>Your PDF is ready.</p>
      <a id="j2p-download" class="btn btn-primary" download="converted.pdf">Download PDF</a>
    </div>
    """
    script = """
    (function(){
      var files = []; // {file, rotation}
      var dz = document.getElementById('j2p-dropzone');
      var input = document.getElementById('j2p-file');
      var listEl = document.getElementById('j2p-list');
      var genBtn = document.getElementById('j2p-generate');
      function showError(msg){
        var box = document.getElementById('error-box');
        box.textContent = msg; box.classList.remove('hidden');
      }
      function renderList(){
        listEl.innerHTML = '';
        files.forEach(function(entry, i){
          var li = document.createElement('li');
          var label = document.createElement('span');
          label.textContent = (i+1) + '. ' + entry.file.name + (entry.rotation ? ' (rotated ' + entry.rotation + '\u00b0)' : '');
          li.appendChild(label);
          var controls = document.createElement('span');
          controls.style.display = 'flex'; controls.style.gap = '6px';

          var upBtn = document.createElement('button'); upBtn.textContent = '\u2191'; upBtn.className = 'btn btn-ghost'; upBtn.setAttribute('aria-label','Move up');
          upBtn.disabled = i === 0;
          upBtn.addEventListener('click', function(){ if (i>0){ var tmp=files[i-1]; files[i-1]=files[i]; files[i]=tmp; renderList(); } });

          var downBtn = document.createElement('button'); downBtn.textContent = '\u2193'; downBtn.className = 'btn btn-ghost'; downBtn.setAttribute('aria-label','Move down');
          downBtn.disabled = i === files.length-1;
          downBtn.addEventListener('click', function(){ if (i<files.length-1){ var tmp=files[i+1]; files[i+1]=files[i]; files[i]=tmp; renderList(); } });

          var rotBtn = document.createElement('button'); rotBtn.textContent = '\u21bb Rotate'; rotBtn.className = 'btn btn-ghost'; rotBtn.setAttribute('aria-label','Rotate 90 degrees');
          rotBtn.addEventListener('click', function(){ entry.rotation = (entry.rotation + 90) % 360; renderList(); });

          var rmBtn = document.createElement('button'); rmBtn.textContent = 'Remove'; rmBtn.className = 'btn btn-ghost';
          rmBtn.addEventListener('click', function(){ files.splice(i,1); renderList(); });

          controls.appendChild(upBtn); controls.appendChild(downBtn); controls.appendChild(rotBtn); controls.appendChild(rmBtn);
          li.appendChild(controls);
          listEl.appendChild(li);
        });
        genBtn.disabled = files.length === 0;
        document.getElementById('j2p-pagesize-wrap').style.display = files.length ? 'block' : 'none';
      }
      function addFiles(fileList){
        document.getElementById('error-box').classList.add('hidden');
        for (var i=0;i<fileList.length;i++){
          var f = fileList[i];
          if (!/^image\\/(jpeg|png)$/.test(f.type)) { showError('Only JPG and PNG images are supported. Skipped: ' + f.name); continue; }
          if (f.size > 15*1024*1024) { showError('Skipped ' + f.name + ' (over 15 MB).'); continue; }
          files.push({ file: f, rotation: 0 });
        }
        renderList();
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ addFiles(e.dataTransfer.files); });
      input.addEventListener('change', function(){ addFiles(input.files); input.value=''; });

      // Re-draws an image onto a canvas rotated by 0/90/180/270 degrees, returns {bytes, width, height}
      async function rotateImageBytes(file, rotationDeg){
        return new Promise(function(resolve, reject){
          var img = new Image();
          img.onload = function(){
            var canvas = document.createElement('canvas');
            var swap = rotationDeg === 90 || rotationDeg === 270;
            canvas.width = swap ? img.naturalHeight : img.naturalWidth;
            canvas.height = swap ? img.naturalWidth : img.naturalHeight;
            var ctx = canvas.getContext('2d');
            ctx.translate(canvas.width/2, canvas.height/2);
            ctx.rotate(rotationDeg * Math.PI/180);
            ctx.drawImage(img, -img.naturalWidth/2, -img.naturalHeight/2);
            canvas.toBlob(function(blob){
              blob.arrayBuffer().then(function(buf){
                resolve({ bytes: buf, width: canvas.width, height: canvas.height });
              });
            }, 'image/jpeg', 0.92);
          };
          img.onerror = function(){ reject(new Error('bad_image')); };
          var reader = new FileReader();
          reader.onload = function(e){ img.src = e.target.result; };
          reader.readAsDataURL(file);
        });
      }

      genBtn.addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (typeof PDFLib === 'undefined') { showError('The PDF library failed to load. Please check your internet connection and try again.'); return; }
        if (files.length === 0) { showError('Please add at least one image.'); return; }
        genBtn.disabled = true; genBtn.textContent = 'Converting...';
        var pageSizeMode = document.getElementById('j2p-pagesize').value;
        try {
          var pdfDoc = await PDFLib.PDFDocument.create();
          for (var i=0;i<files.length;i++){
            var entry = files[i];
            var imgBytes, w, h;
            if (entry.rotation !== 0) {
              var r = await rotateImageBytes(entry.file, entry.rotation);
              imgBytes = r.bytes; w = r.width; h = r.height;
              var img = await pdfDoc.embedJpg(imgBytes);
              addImagePage(pdfDoc, img, w, h, pageSizeMode);
            } else {
              var bytes = await entry.file.arrayBuffer();
              var img2 = entry.file.type === 'image/png' ? await pdfDoc.embedPng(bytes) : await pdfDoc.embedJpg(bytes);
              addImagePage(pdfDoc, img2, img2.width, img2.height, pageSizeMode);
            }
          }
          var pdfBytes = await pdfDoc.save();
          var blob = new Blob([pdfBytes], {type:'application/pdf'});
          var url = URL.createObjectURL(blob);
          document.getElementById('j2p-download').href = url;
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          showError('Something went wrong converting these images. Please try different files.');
        } finally {
          genBtn.disabled = false; genBtn.textContent = 'Convert to PDF';
        }
      });

      function addImagePage(pdfDoc, img, w, h, mode){
        if (mode === 'a4') {
          var pageW = 595.28, pageH = 841.89; // A4 in points
          var scale = Math.min((pageW-40)/w, (pageH-40)/h, 1);
          var drawW = w*scale, drawH = h*scale;
          var page = pdfDoc.addPage([pageW, pageH]);
          page.drawImage(img, { x:(pageW-drawW)/2, y:(pageH-drawH)/2, width:drawW, height:drawH });
        } else {
          var page2 = pdfDoc.addPage([w, h]);
          page2.drawImage(img, {x:0, y:0, width:w, height:h});
        }
      }

      document.getElementById('j2p-reset').addEventListener('click', function(){
        files = []; renderList();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "jpg-to-pdf", panel, script,
        how_it_works="<p>Each image you add is embedded onto its own page of a new PDF document, built entirely in your browser using an open-source PDF library. You can reorder pages with the up/down buttons, rotate any image in 90&deg; steps before conversion, and choose whether each page matches the image's original size or is centered on a standard A4 page. No image is uploaded to a server at any point.</p>",
        example="<p>Add three photos, use \u2191/\u2193 to put them in the right order, rotate a sideways photo 90&deg;, choose 'Fit page to each image', and download a single 3-page PDF.</p>",
        faqs=[
            ("Can I reorder images before converting?", "Yes &mdash; use the \u2191 and \u2193 buttons next to each file to move it up or down in the list before converting."),
            ("Can I rotate a photo that's sideways?", "Yes, click 'Rotate' on that image as many times as needed (each click adds 90&deg;) before converting."),
            ("Should I choose 'original size' or 'A4'?", "Use 'Fit page to each image' if you want each PDF page to exactly match its photo's proportions. Use 'A4' if you need consistent, standard page sizes for printing."),
            ("Is there a file size limit?", "Each image can be up to 15 MB. Very large numbers of high-resolution images may be slow to process depending on your device."),
        ],
        related_override=[t for t in tools if t['slug'] in ('merge-pdf','pdf-to-jpg','compress-pdf','image-compressor')],
        extra_head=PDF_LIB_SCRIPT,
    )

    # ---------------- Merge PDF ----------------
    panel = """
    <div id="mp-dropzone" class="drop-zone">
      <p><strong>Drag & drop PDF files here</strong>, or</p>
      <label class="btn btn-secondary" for="mp-file" style="display:inline-flex;margin-top:6px">Choose PDF files</label>
      <input id="mp-file" type="file" accept="application/pdf" multiple style="display:none">
      <p class="search-hint">Add 2 or more PDFs, up to 25 MB each. Processed entirely in your browser.</p>
    </div>
    <ul id="mp-list" class="file-list"></ul>
    <div id="error-box" class="error-msg hidden"></div>
    <div class="row-actions" style="margin-top:14px">
      <button type="button" id="mp-generate" class="btn btn-primary" disabled>Merge PDFs</button>
      <button type="button" id="mp-reset" class="btn btn-secondary">Clear all</button>
    </div>
    <div id="result-box" class="result-card hidden">
      <p>Your merged PDF is ready.</p>
      <a id="mp-download" class="btn btn-primary" download="merged.pdf">Download merged PDF</a>
    </div>
    """
    script = """
    (function(){
      var files = [];
      var dz = document.getElementById('mp-dropzone');
      var input = document.getElementById('mp-file');
      var listEl = document.getElementById('mp-list');
      var genBtn = document.getElementById('mp-generate');
      function showError(msg){
        var box = document.getElementById('error-box');
        box.textContent = msg; box.classList.remove('hidden');
      }
      function renderList(){
        listEl.innerHTML = '';
        files.forEach(function(f,i){
          var li = document.createElement('li');
          li.innerHTML = '<span>' + (i+1) + '. ' + f.name + '</span>';
          var btn = document.createElement('button');
          btn.textContent = 'Remove'; btn.className='btn btn-ghost';
          btn.addEventListener('click', function(){ files.splice(i,1); renderList(); });
          li.appendChild(btn);
          listEl.appendChild(li);
        });
        genBtn.disabled = files.length < 2;
      }
      function addFiles(fileList){
        document.getElementById('error-box').classList.add('hidden');
        for (var i=0;i<fileList.length;i++){
          var f = fileList[i];
          if (f.type !== 'application/pdf') { showError('Only PDF files are supported. Skipped: ' + f.name); continue; }
          if (f.size > 25*1024*1024) { showError('Skipped ' + f.name + ' (over 25 MB).'); continue; }
          files.push(f);
        }
        renderList();
      }
      ['dragover','dragenter'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); }); });
      ['dragleave','drop'].forEach(function(evt){ dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); }); });
      dz.addEventListener('drop', function(e){ addFiles(e.dataTransfer.files); });
      input.addEventListener('change', function(){ addFiles(input.files); input.value=''; });

      genBtn.addEventListener('click', async function(){
        document.getElementById('error-box').classList.add('hidden');
        if (typeof PDFLib === 'undefined') { showError('The PDF library failed to load. Please check your internet connection and try again.'); return; }
        if (files.length < 2) { showError('Please add at least two PDF files to merge.'); return; }
        genBtn.disabled = true; genBtn.textContent = 'Merging...';
        try {
          var mergedPdf = await PDFLib.PDFDocument.create();
          for (var i=0;i<files.length;i++){
            var bytes = await files[i].arrayBuffer();
            var src = await PDFLib.PDFDocument.load(bytes, {ignoreEncryption:true});
            var pages = await mergedPdf.copyPages(src, src.getPageIndices());
            pages.forEach(function(p){ mergedPdf.addPage(p); });
          }
          var pdfBytes = await mergedPdf.save();
          var blob = new Blob([pdfBytes], {type:'application/pdf'});
          var url = URL.createObjectURL(blob);
          document.getElementById('mp-download').href = url;
          document.getElementById('result-box').classList.remove('hidden');
        } catch (err) {
          showError('One of these PDFs could not be read (it may be corrupted or password-protected). Please check the files and try again.');
        } finally {
          genBtn.disabled = false; genBtn.textContent = 'Merge PDFs';
        }
      });
      document.getElementById('mp-reset').addEventListener('click', function(){
        files = []; renderList();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "merge-pdf", panel, script,
        how_it_works="<p>Each PDF you add is read and its pages are copied, in order, into one new PDF document &mdash; entirely inside your browser using an open-source PDF library. Files are never uploaded to a server.</p>",
        example="<p>Add report-part1.pdf and report-part2.pdf, merge, and download a single combined PDF with all pages from both files in order.</p>",
        faqs=[
            ("Can I merge password-protected PDFs?", "Encrypted or password-protected PDFs generally cannot be read by the browser-based library used here. Remove the password first using a PDF editor, then merge."),
            ("Is there a limit on how many files I can merge?", "There's no hard limit, but very large or numerous PDFs may be slow to process depending on your device's memory."),
        ],
        extra_head=PDF_LIB_SCRIPT,
    )
