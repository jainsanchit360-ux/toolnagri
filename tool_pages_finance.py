from build import build_tool_page

def register():
    # ---------------- EMI Calculator ----------------
    panel = """
    <form id="emi-form">
      <div class="field"><label for="emi-principal">Loan amount (&#8377;)</label><input id="emi-principal" type="number" min="0" step="1000" placeholder="1000000" required></div>
      <div class="field"><label for="emi-rate">Annual interest rate (%)</label><input id="emi-rate" type="number" min="0" step="0.01" placeholder="9.5" required></div>
      <div class="field"><label for="emi-tenure">Loan tenure (years)</label><input id="emi-tenure" type="number" min="0" step="0.5" placeholder="20" required></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate EMI</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Monthly EMI</div>
      <div class="big" id="emi-value">&#8377;0</div>
      <div class="result-grid">
        <div class="item"><div class="label">Total interest payable</div><div class="val" id="emi-interest">-</div></div>
        <div class="item"><div class="label">Total payment (principal + interest)</div><div class="val" id="emi-total">-</div></div>
      </div>
      <div class="row-actions" style="margin-top:14px"><button type="button" id="copy-btn" class="btn btn-secondary">Copy result</button></div>
    </div>
    """
    script = """
    (function(){
      function inr(n){ return '\u20b9' + n.toLocaleString('en-IN', {maximumFractionDigits:0}); }
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('emi-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var P = parseFloat(document.getElementById('emi-principal').value);
        var annualRate = parseFloat(document.getElementById('emi-rate').value);
        var years = parseFloat(document.getElementById('emi-tenure').value);
        if ([P,annualRate,years].some(isNaN)) { showError('Please fill in loan amount, interest rate and tenure.'); return; }
        if (P <= 0 || years <= 0) { showError('Loan amount and tenure must be greater than zero.'); return; }
        if (annualRate < 0) { showError('Interest rate cannot be negative.'); return; }
        if (P > 1e12) { showError('That loan amount looks unrealistically large. Please check the value.'); return; }
        var n = Math.round(years * 12);
        var r = (annualRate/12)/100;
        var emi;
        if (r === 0) {
          emi = P / n;
        } else {
          var pow = Math.pow(1+r, n);
          emi = P * r * pow / (pow - 1);
        }
        var total = emi * n;
        var interest = total - P;
        document.getElementById('emi-value').textContent = inr(emi);
        document.getElementById('emi-interest').textContent = inr(interest);
        document.getElementById('emi-total').textContent = inr(total);
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('emi-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
      document.getElementById('copy-btn').addEventListener('click', function(){
        window.ToolNagri.copyText('Monthly EMI: ' + document.getElementById('emi-value').textContent, this);
      });
    })();
    """
    build_tool_page(
        "emi-calculator", panel, script,
        how_it_works="<p>EMI (Equated Monthly Instalment) is calculated using the standard reducing-balance loan formula:</p><p><strong>EMI = P &times; r &times; (1+r)<sup>n</sup> &divide; ((1+r)<sup>n</sup> - 1)</strong></p><p>where P is the principal (loan amount), r is the monthly interest rate (annual rate &divide; 12 &divide; 100), and n is the number of monthly instalments (tenure in years &times; 12).</p>",
        example="<p>A &#8377;10,00,000 loan at 9.5% annual interest for 20 years works out to an EMI of roughly &#8377;9,320 per month, with total interest of about &#8377;12.4 lakh over the loan's life.</p>",
        faqs=[
            ("Does this include processing fees or insurance?", "No. This calculates the pure EMI on principal and interest. Banks may add processing fees, insurance premiums or other charges separately."),
            ("What if my loan has a floating interest rate?", "Enter the current rate to get today's EMI estimate. Floating-rate EMIs will change if the bank revises the rate; re-run the calculator with the new rate to see the updated figure."),
            ("Is this financial advice?", "No, this is an educational estimate based on standard EMI formulas, not financial advice. Confirm exact figures with your lender."),
        ],
        disclaimer="This is an educational estimate, not a loan offer or financial advice. Actual EMI may vary based on your lender's terms, fees and rounding methods.",
    )

    # ---------------- SIP Calculator ----------------
    panel = """
    <form id="sip-form">
      <div class="field"><label for="sip-amount">Monthly investment (&#8377;)</label><input id="sip-amount" type="number" min="0" step="500" placeholder="5000" required></div>
      <div class="field"><label for="sip-return">Expected annual return (%)</label><input id="sip-return" type="number" min="0" step="0.1" placeholder="12" required></div>
      <div class="field"><label for="sip-years">Investment duration (years)</label><input id="sip-years" type="number" min="0" step="0.5" placeholder="10" required></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Estimated maturity value</div>
      <div class="big" id="sip-value">&#8377;0</div>
      <div class="result-grid">
        <div class="item"><div class="label">Total invested</div><div class="val" id="sip-invested">-</div></div>
        <div class="item"><div class="label">Estimated returns</div><div class="val" id="sip-returns">-</div></div>
      </div>
    </div>
    """
    script = """
    (function(){
      function inr(n){ return '\u20b9' + Math.round(n).toLocaleString('en-IN'); }
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('sip-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var amt = parseFloat(document.getElementById('sip-amount').value);
        var rate = parseFloat(document.getElementById('sip-return').value);
        var years = parseFloat(document.getElementById('sip-years').value);
        if ([amt,rate,years].some(isNaN)) { showError('Please fill in all fields.'); return; }
        if (amt <= 0 || years <= 0) { showError('Monthly investment and duration must be greater than zero.'); return; }
        if (rate < 0) { showError('Expected return cannot be negative.'); return; }
        var n = Math.round(years*12);
        var i = rate/12/100;
        var futureValue;
        if (i === 0) {
          futureValue = amt * n;
        } else {
          futureValue = amt * ((Math.pow(1+i,n) - 1) / i) * (1+i);
        }
        var invested = amt * n;
        var returns = futureValue - invested;
        document.getElementById('sip-value').textContent = inr(futureValue);
        document.getElementById('sip-invested').textContent = inr(invested);
        document.getElementById('sip-returns').textContent = inr(returns);
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('sip-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "sip-calculator", panel, script,
        how_it_works="<p>SIP (Systematic Investment Plan) maturity value is estimated using the future value of a series formula, assuming monthly compounding of the expected annual return:</p><p><strong>FV = P &times; [((1+i)<sup>n</sup> - 1) &divide; i] &times; (1+i)</strong></p><p>where P is the monthly investment, i is the monthly rate of return, and n is the number of months.</p>",
        example="<p>Investing &#8377;5,000 per month for 10 years at an expected 12% annual return gives an estimated maturity value of around &#8377;11.6 lakh, of which about &#8377;6 lakh is your own invested capital and the rest is estimated growth.</p>",
        faqs=[
            ("Is the return guaranteed?", "No. Mutual fund and market-linked SIP returns are never guaranteed. This calculator uses the rate you enter purely as an estimate; actual returns depend on market performance."),
            ("Does this account for expense ratio or exit load?", "No, this is a simplified estimate based on your expected gross return. Actual net returns will be lower after fund expenses and taxes."),
        ],
        disclaimer="Mutual fund investments are subject to market risk. This tool provides an educational estimate only, not investment advice.",
    )

    # ---------------- GST Calculator ----------------
    panel = """
    <form id="gst-form">
      <div class="field"><label for="gst-amount">Amount (&#8377;)</label><input id="gst-amount" type="number" min="0" step="1" placeholder="10000" required></div>
      <div class="field"><label for="gst-rate">GST rate (%)</label>
        <select id="gst-rate">
          <option value="5">5%</option>
          <option value="12">12%</option>
          <option value="18" selected>18%</option>
          <option value="28">28%</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      <div class="field" id="gst-custom-wrap" style="display:none"><label for="gst-custom">Custom GST rate (%)</label><input id="gst-custom" type="number" min="0" step="0.1"></div>
      <div class="field">
        <label for="gst-type">Calculation type</label>
        <select id="gst-type">
          <option value="exclusive">Add GST (amount is before tax)</option>
          <option value="inclusive">Remove GST (amount already includes tax)</option>
        </select>
      </div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="result-grid">
        <div class="item"><div class="label">Base amount</div><div class="val" id="gst-base">-</div></div>
        <div class="item"><div class="label">CGST</div><div class="val" id="gst-cgst">-</div></div>
        <div class="item"><div class="label">SGST</div><div class="val" id="gst-sgst">-</div></div>
        <div class="item"><div class="label">Total (incl. GST)</div><div class="val" id="gst-total">-</div></div>
      </div>
    </div>
    """
    script = """
    (function(){
      function inr(n){ return '\u20b9' + n.toLocaleString('en-IN', {maximumFractionDigits:2}); }
      var rateSel = document.getElementById('gst-rate');
      rateSel.addEventListener('change', function(){
        document.getElementById('gst-custom-wrap').style.display = rateSel.value === 'custom' ? 'block' : 'none';
      });
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('gst-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var amount = parseFloat(document.getElementById('gst-amount').value);
        var rate = rateSel.value === 'custom' ? parseFloat(document.getElementById('gst-custom').value) : parseFloat(rateSel.value);
        var type = document.getElementById('gst-type').value;
        if (isNaN(amount) || isNaN(rate)) { showError('Please enter a valid amount and GST rate.'); return; }
        if (amount < 0 || rate < 0) { showError('Amount and GST rate cannot be negative.'); return; }
        var base, gstAmount, total;
        if (type === 'exclusive') {
          base = amount;
          gstAmount = base * rate/100;
          total = base + gstAmount;
        } else {
          total = amount;
          base = total / (1 + rate/100);
          gstAmount = total - base;
        }
        document.getElementById('gst-base').textContent = inr(base);
        document.getElementById('gst-cgst').textContent = inr(gstAmount/2);
        document.getElementById('gst-sgst').textContent = inr(gstAmount/2);
        document.getElementById('gst-total').textContent = inr(total);
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('gst-form').reset();
        document.getElementById('gst-custom-wrap').style.display = 'none';
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "gst-calculator", panel, script,
        how_it_works="<p>To add GST to a base amount: GST = Base &times; Rate &divide; 100, Total = Base + GST. To remove GST from a tax-inclusive amount: Base = Total &divide; (1 + Rate/100). For intra-state transactions, GST is typically split equally into CGST and SGST; for inter-state transactions, the full amount is charged as IGST.</p>",
        example="<p>For a &#8377;10,000 base amount at 18% GST: GST amount is &#8377;1,800 (split as &#8377;900 CGST + &#8377;900 SGST), giving a total of &#8377;11,800.</p>",
        faqs=[
            ("When is GST split into CGST and SGST vs IGST?", "CGST + SGST applies to intra-state sales (buyer and seller in the same state), split equally. IGST applies to inter-state sales, charged as a single tax by the central government and then apportioned. This calculator shows the CGST/SGST split for intra-state use; for IGST, use the full GST amount shown as 'CGST + SGST' combined."),
            ("What are the common GST slabs in India?", "As of recent years, common GST slabs are 5%, 12%, 18% and 28%, with some items at 0% or special rates. Rates are set by the GST Council and can change; always verify the current rate for your specific goods/service."),
        ],
        disclaimer="GST rates and rules can change. This calculator applies the rate you enter and does not verify it against current government notifications.",
    )
