from build import build_tool_page

def register():
    # ---------------- SGPA Calculator ----------------
    panel = """
    <form id="sgpa-form">
      <div id="subject-rows">
        <div class="subject-row">
          <div class="field"><label>Subject name<input type="text" class="subj-name" placeholder="e.g. Mathematics" required></label></div>
          <div class="field"><label>Credits<input type="number" class="subj-credits" min="0" step="0.5" placeholder="4" required></label></div>
          <div class="field"><label>Grade point (0-10)<input type="number" class="subj-gp" min="0" max="10" step="0.1" placeholder="9" required></label></div>
          <button type="button" class="icon-btn remove-row" aria-label="Remove subject">&times;</button>
        </div>
      </div>
      <div class="row-actions">
        <button type="button" id="add-row" class="btn btn-secondary">+ Add subject</button>
        <button type="submit" class="btn btn-primary">Calculate SGPA</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
      <p class="field hint">Uses the standard 10-point scale (grade point &times; credits, summed, divided by total credits). If your institute uses letter grades, convert to grade points first &mdash; most Indian universities publish a grade-to-point table (e.g. O=10, A+=9, A=8&hellip;).</p>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Your SGPA</div>
      <div class="big" id="sgpa-value">0.00</div>
      <div class="result-grid">
        <div class="item"><div class="label">Total credits</div><div class="val" id="total-credits">-</div></div>
        <div class="item"><div class="label">Weighted points</div><div class="val" id="weighted-points">-</div></div>
      </div>
      <div class="row-actions" style="margin-top:14px">
        <button type="button" id="copy-btn" class="btn btn-secondary">Copy result</button>
      </div>
    </div>
    """
    script = """
    (function(){
      var rowsEl = document.getElementById('subject-rows');
      var rowTemplate = rowsEl.children[0].outerHTML;
      document.getElementById('add-row').addEventListener('click', function(){
        rowsEl.insertAdjacentHTML('beforeend', rowTemplate);
      });
      rowsEl.addEventListener('click', function(e){
        if (e.target.classList.contains('remove-row')) {
          if (rowsEl.children.length > 1) e.target.closest('.subject-row').remove();
        }
      });
      function showError(msg){
        var box = document.getElementById('error-box');
        box.textContent = msg; box.classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('sgpa-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var rows = rowsEl.querySelectorAll('.subject-row');
        var totalCredits = 0, weighted = 0, count = 0;
        for (var i=0;i<rows.length;i++){
          var credits = parseFloat(rows[i].querySelector('.subj-credits').value);
          var gp = parseFloat(rows[i].querySelector('.subj-gp').value);
          if (isNaN(credits) || isNaN(gp)) continue;
          if (credits < 0 || gp < 0) { showError('Credits and grade points cannot be negative.'); return; }
          if (gp > 10) { showError('Grade point cannot be greater than 10 on the standard scale.'); return; }
          totalCredits += credits; weighted += credits * gp; count++;
        }
        if (count === 0) { showError('Please enter at least one subject with valid credits and grade point.'); return; }
        if (totalCredits === 0) { showError('Total credits cannot be zero.'); return; }
        var sgpa = weighted / totalCredits;
        document.getElementById('sgpa-value').textContent = sgpa.toFixed(2);
        document.getElementById('total-credits').textContent = totalCredits;
        document.getElementById('weighted-points').textContent = weighted.toFixed(2);
        document.getElementById('result-box').classList.remove('hidden');
        window.ToolNagri && window.ToolNagri.track('calculation_completed', {tool:'sgpa-calculator'});
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('sgpa-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        while (rowsEl.children.length > 1) rowsEl.removeChild(rowsEl.lastChild);
      });
      document.getElementById('copy-btn').addEventListener('click', function(){
        var v = document.getElementById('sgpa-value').textContent;
        window.ToolNagri.copyText('My SGPA: ' + v, this);
      });
    })();
    """
    build_tool_page(
        "sgpa-calculator", panel, script,
        how_it_works="<p>SGPA (Semester Grade Point Average) is calculated by multiplying each subject's grade point by its credit value, adding these up across all subjects, and dividing by the total number of credits for the semester.</p><p><strong>Formula:</strong> SGPA = &sum;(Credit &times; Grade Point) &divide; &sum;(Credit)</p>",
        example="<p>If you have 3 subjects &mdash; 4 credits at grade point 9, 3 credits at grade point 8, and 4 credits at grade point 7 &mdash; your SGPA is (4&times;9 + 3&times;8 + 4&times;7) &divide; (4+3+4) = 88 &divide; 11 = <strong>8.00</strong>.</p>",
        faqs=[
            ("What is SGPA?", "SGPA stands for Semester Grade Point Average, a weighted average of grade points earned in a single semester, weighted by subject credits."),
            ("Is this the same for all Indian universities?", "The credit-weighted formula is standard, but the grade-to-point mapping (e.g. what grade point an 'A' equals) varies by institution. Check your university's official grading table before relying on the result for official purposes."),
            ("Can grade points be more than 10?", "Most Indian universities use a 10-point scale, so this calculator caps grade points at 10. If your institution uses a different scale, adjust your inputs proportionally."),
        ],
        disclaimer="This calculator uses the standard credit-weighted formula. Always confirm against your university's official grading policy for results used in official records.",
    )

    # ---------------- CGPA Calculator ----------------
    panel = """
    <form id="cgpa-form">
      <div id="sem-rows">
        <div class="subject-row" style="grid-template-columns:1fr 1fr 1fr auto">
          <div class="field"><label>Semester<input type="text" class="sem-name" placeholder="Semester 1" required></label></div>
          <div class="field"><label>SGPA<input type="number" class="sem-sgpa" min="0" max="10" step="0.01" placeholder="8.5" required></label></div>
          <div class="field"><label>Credits<input type="number" class="sem-credits" min="0" step="0.5" placeholder="22" required></label></div>
          <button type="button" class="icon-btn remove-row" aria-label="Remove semester">&times;</button>
        </div>
      </div>
      <div class="row-actions">
        <button type="button" id="add-row" class="btn btn-secondary">+ Add semester</button>
        <button type="submit" class="btn btn-primary">Calculate CGPA</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Your CGPA</div>
      <div class="big" id="cgpa-value">0.00</div>
      <div class="result-grid">
        <div class="item"><div class="label">Total credits</div><div class="val" id="total-credits">-</div></div>
        <div class="item"><div class="label">Equivalent percentage (approx.)</div><div class="val" id="cgpa-pct">-</div></div>
      </div>
    </div>
    """
    script = """
    (function(){
      var rowsEl = document.getElementById('sem-rows');
      var tmpl = rowsEl.children[0].outerHTML;
      document.getElementById('add-row').addEventListener('click', function(){
        rowsEl.insertAdjacentHTML('beforeend', tmpl);
      });
      rowsEl.addEventListener('click', function(e){
        if (e.target.classList.contains('remove-row') && rowsEl.children.length > 1) e.target.closest('.subject-row').remove();
      });
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('cgpa-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var rows = rowsEl.querySelectorAll('.subject-row');
        var totalCredits=0, weighted=0, count=0;
        for (var i=0;i<rows.length;i++){
          var sgpa = parseFloat(rows[i].querySelector('.sem-sgpa').value);
          var credits = parseFloat(rows[i].querySelector('.sem-credits').value);
          if (isNaN(sgpa) || isNaN(credits)) continue;
          if (sgpa < 0 || credits < 0) { showError('SGPA and credits cannot be negative.'); return; }
          if (sgpa > 10) { showError('SGPA cannot be greater than 10 on the standard scale.'); return; }
          totalCredits += credits; weighted += sgpa*credits; count++;
        }
        if (count===0){ showError('Please enter at least one semester with valid SGPA and credits.'); return; }
        if (totalCredits===0){ showError('Total credits cannot be zero.'); return; }
        var cgpa = weighted/totalCredits;
        document.getElementById('cgpa-value').textContent = cgpa.toFixed(2);
        document.getElementById('total-credits').textContent = totalCredits;
        document.getElementById('cgpa-pct').textContent = (cgpa*9.5).toFixed(1) + '%';
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('cgpa-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
        while (rowsEl.children.length > 1) rowsEl.removeChild(rowsEl.lastChild);
      });
    })();
    """
    build_tool_page(
        "cgpa-calculator", panel, script,
        how_it_works="<p>CGPA (Cumulative Grade Point Average) is the credit-weighted average of your SGPA across all completed semesters.</p><p><strong>Formula:</strong> CGPA = &sum;(SGPA &times; Semester Credits) &divide; &sum;(Semester Credits)</p>",
        example="<p>Semester 1: SGPA 8.5 with 22 credits. Semester 2: SGPA 7.8 with 24 credits. CGPA = (8.5&times;22 + 7.8&times;24) &divide; (22+24) = 374.2 &divide; 46 = <strong>8.13</strong>.</p>",
        faqs=[
            ("How do I convert CGPA to percentage?", "A commonly used approximation (used by many Indian universities, including AICTE-affiliated ones) is Percentage = CGPA &times; 9.5. This calculator shows that estimate, but always check your specific university's official formula."),
            ("Does CGPA include backlog subjects?", "This depends on your institution's policy on how repeated/backlog subjects are averaged. This calculator simply averages whatever SGPA and credit values you enter."),
        ],
        disclaimer="The CGPA-to-percentage conversion (&times;9.5) is a common approximation, not a universal rule. Confirm with your university for official use.",
    )

    # ---------------- Attendance Calculator ----------------
    panel = """
    <form id="att-form">
      <div class="field"><label for="att-attended">Classes attended</label><input id="att-attended" type="number" min="0" step="1" required></div>
      <div class="field"><label for="att-total">Total classes held</label><input id="att-total" type="number" min="0" step="1" required></div>
      <div class="field"><label for="att-target">Desired attendance % (e.g. 75)</label><input id="att-target" type="number" min="1" max="100" step="0.1" value="75" required></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Current attendance</div>
      <div class="big" id="current-pct">0%</div>
      <p id="verdict-text" style="margin-top:10px;font-weight:600"></p>
    </div>
    """
    script = """
    (function(){
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('att-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var attended = parseFloat(document.getElementById('att-attended').value);
        var total = parseFloat(document.getElementById('att-total').value);
        var target = parseFloat(document.getElementById('att-target').value);
        if ([attended,total,target].some(isNaN)) { showError('Please fill in all three fields with numbers.'); return; }
        if (attended < 0 || total < 0 || target <= 0) { showError('Values cannot be negative, and target attendance must be greater than 0.'); return; }
        if (attended > total) { showError('Classes attended cannot be greater than total classes held.'); return; }
        if (target > 100) { showError('Target attendance cannot be more than 100%.'); return; }
        var current = total === 0 ? 0 : (attended/total)*100;
        document.getElementById('current-pct').textContent = current.toFixed(2) + '%';
        var verdict = '';
        if (total === 0) {
          verdict = 'No classes recorded yet.';
        } else if (current >= target) {
          // how many classes can be skipped while staying at/above target
          // (attended) / (total + x) >= target/100  => x <= attended*100/target - total
          var maxSkip = Math.floor((attended*100/target) - total);
          maxSkip = Math.max(maxSkip, 0);
          verdict = 'You are already above your ' + target + '% target. You can miss up to ' + maxSkip + ' more class' + (maxSkip===1?'':'es') + ' in a row (assuming no more classes are added) and stay at or above ' + target + '%.';
        } else {
          // (attended + x) / (total + x) >= target/100
          // attended + x >= target/100 * (total + x)
          // x (1 - target/100) >= target/100*total - attended
          var t = target/100;
          if (t >= 1) { showError('A 100% target requires attending every remaining class from now on.'); return; }
          var need = (t*total - attended) / (1 - t);
          need = Math.ceil(need);
          if (need < 0) need = 0;
          verdict = 'You need to attend ' + need + ' more class' + (need===1?'':'es') + ' in a row (with no absences) to reach ' + target + '%.';
        }
        document.getElementById('verdict-text').textContent = verdict;
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('att-form').reset();
        document.getElementById('att-target').value = 75;
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "attendance-calculator", panel, script,
        how_it_works="<p>Your current attendance percentage is (classes attended &divide; total classes) &times; 100. If you're below your target, we calculate how many consecutive future classes you'd need to attend (assuming no more are missed) to reach it. If you're already above target, we calculate how many classes you could still miss while staying at or above it.</p>",
        example="<p>You've attended 60 of 80 classes (75%). To reach 80% attendance, you would need to attend about 20 more classes in a row without missing any, assuming no further classes are conducted in between.</p>",
        faqs=[
            ("Why is 75% attendance so common in India?", "Many Indian universities and colleges (including AICTE/UGC-affiliated institutions) require a minimum of 75% attendance to be eligible to sit for exams, though the exact rule varies by institution."),
            ("What if reaching my target is mathematically impossible?", "If the target is very high (like 100%) and you've already missed classes, the calculator will tell you that only attending every remaining class can help, or that the target isn't achievable with classes held so far."),
        ],
    )
