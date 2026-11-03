/**
 * BongoBazaar - Payment Gateway Simulation Engine
 * Handles interactive bKash, Nagad, Rocket, Card, and Cash On Delivery UI modals
 */

const PaymentGateway = {
    currentMethod: 'COD',
    verifiedTrxId: null,
    onSuccessCallback: null,

    init(onSuccess) {
        this.onSuccessCallback = onSuccess;
        this.setupEventListeners();
    },

    setupEventListeners() {
        const methodRadios = document.querySelectorAll('input[name="payment_method"]');
        methodRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentMethod = e.target.value;
                this.updatePaymentView();
            });
        });
    },

    updatePaymentView() {
        const detailsContainer = document.getElementById('payment-method-details');
        if (!detailsContainer) return;

        let content = '';

        if (this.currentMethod === 'bKash') {
            content = `
            <div class="p-4 rounded-xl border-2 border-pink-500 bg-pink-50/50">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-pink-600 animate-pulse"></span>
                        <h4 class="font-bold text-pink-700">বিকাশ অনলাইন পেমেন্ট (bKash Checkout)</h4>
                    </div>
                    <span class="text-xs font-bold px-2 py-0.5 rounded bg-pink-600 text-white">ইনস্ট্যান্ট ভেরিফিকেশন</span>
                </div>
                <p class="text-xs text-slate-600 mb-3">
                    বিকাশ মার্চেন্ট একাউন্টে পেমেন্ট করুন অথবা আমাদের ইনস্ট্যান্ট গেটওয়ে পপআপের মাধ্যমে পিন দিয়ে সম্পন্ন করুন।
                </p>
                <div class="bg-white p-3 rounded-lg border border-pink-200 mb-3 text-xs flex justify-between items-center">
                    <div>
                        <span class="text-slate-500 block">মার্চেন্ট নম্বর:</span>
                        <span class="font-mono font-bold text-slate-800 text-sm">01711-000001 (মার্চেন্ট)</span>
                    </div>
                    <button type="button" onclick="navigator.clipboard.writeText('01711000001'); showToast('কপি হয়েছে', 'বিকাশ নম্বর ক্লিপবোর্ডে কপি হয়েছে', 'info')" class="text-pink-600 hover:text-pink-700 font-semibold">কপি</button>
                </div>
                <div class="space-y-2">
                    <label class="block text-xs font-semibold text-slate-700">বিকাশ ট্রানজেকশন আইডি (TrxID) দিন:</label>
                    <div class="flex gap-2">
                        <input type="text" id="bkash-trxid" placeholder="যেমন: BKASH8921XYZ" class="flex-1 uppercase font-mono px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-pink-500 outline-none">
                        <button type="button" onclick="PaymentGateway.simulateBkashModal()" class="px-4 py-2 bg-pink-600 hover:bg-pink-700 text-white text-xs font-bold rounded-lg whitespace-nowrap shadow-sm">
                            অটো পে (bKash)
                        </button>
                    </div>
                </div>
            </div>
            `;
        } else if (this.currentMethod === 'Nagad') {
            content = `
            <div class="p-4 rounded-xl border-2 border-amber-500 bg-amber-50/50">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-amber-600 animate-pulse"></span>
                        <h4 class="font-bold text-amber-800">নগদ অনলাইন পেমেন্ট (Nagad Checkout)</h4>
                    </div>
                    <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-600 text-white">ইনস্ট্যান্ট</span>
                </div>
                <p class="text-xs text-slate-600 mb-3">
                    নগদ মার্চেন্ট নম্বরে পেমেন্ট করে ট্রানজেকশন আইডি প্রদান করুন অথবা অটো-গেটওয়ে সিলেক্ট করুন।
                </p>
                <div class="bg-white p-3 rounded-lg border border-amber-200 mb-3 text-xs flex justify-between items-center">
                    <div>
                        <span class="text-slate-500 block">নগদ মার্চেন্ট নম্বর:</span>
                        <span class="font-mono font-bold text-slate-800 text-sm">01819-000002 (মার্চেন্ট)</span>
                    </div>
                    <button type="button" onclick="navigator.clipboard.writeText('01819000002'); showToast('কপি হয়েছে', 'নগদ নম্বর ক্লিপবোর্ডে কপি হয়েছে', 'info')" class="text-amber-700 hover:text-amber-800 font-semibold">কপি</button>
                </div>
                <div class="space-y-2">
                    <label class="block text-xs font-semibold text-slate-700">নগদ ট্রানজেকশন আইডি (TrxID) দিন:</label>
                    <div class="flex gap-2">
                        <input type="text" id="nagad-trxid" placeholder="যেমন: NAGAD123456" class="flex-1 uppercase font-mono px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-amber-500 outline-none">
                        <button type="button" onclick="PaymentGateway.simulateNagadModal()" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg whitespace-nowrap shadow-sm">
                            অটো পে (নগদ)
                        </button>
                    </div>
                </div>
            </div>
            `;
        } else if (this.currentMethod === 'Rocket') {
            content = `
            <div class="p-4 rounded-xl border-2 border-purple-500 bg-purple-50/50">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="font-bold text-purple-900">ডাচ-বাংলা রকেট (Rocket)</h4>
                    <span class="text-xs font-bold px-2 py-0.5 rounded bg-purple-700 text-white">DBBL</span>
                </div>
                <p class="text-xs text-slate-600 mb-2">
                    রকেট বিলার আইডি: <strong class="font-mono">2481 (BongoBazaar)</strong>
                </p>
                <div class="space-y-2">
                    <label class="block text-xs font-semibold text-slate-700">রকেট ট্রানজেকশন আইডি:</label>
                    <input type="text" id="rocket-trxid" placeholder="রকেট ট্রানজেকশন আইডি লিখুন" class="w-full uppercase font-mono px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-purple-500 outline-none">
                </div>
            </div>
            `;
        } else if (this.currentMethod === 'Card') {
            content = `
            <div class="p-4 rounded-xl border-2 border-slate-700 bg-slate-50">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="font-bold text-slate-800">ভিসা / মাস্টারকার্ড / এমেক্স কার্ড পেমেন্ট</h4>
                    <div class="flex gap-1">
                        <span class="px-1.5 py-0.5 bg-blue-600 text-white text-[10px] font-bold rounded">VISA</span>
                        <span class="px-1.5 py-0.5 bg-red-600 text-white text-[10px] font-bold rounded">MC</span>
                    </div>
                </div>
                <div class="space-y-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">কার্ডহোল্ডারের নাম</label>
                        <input type="text" id="card-name" placeholder="MD. RAHIM" class="w-full px-3 py-2 text-sm border rounded-lg uppercase outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">কার্ড নম্বর (১৬ ডিজিট)</label>
                        <input type="text" id="card-number" placeholder="4123 4567 8901 2345" maxlength="19" class="w-full px-3 py-2 text-sm border rounded-lg font-mono outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">মেয়াদ (MM/YY)</label>
                            <input type="text" id="card-expiry" placeholder="12/28" maxlength="5" class="w-full px-3 py-2 text-sm border rounded-lg font-mono outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 mb-1">CVV / CVC</label>
                            <input type="password" id="card-cvv" placeholder="•••" maxlength="4" class="w-full px-3 py-2 text-sm border rounded-lg font-mono outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                </div>
            </div>
            `;
        } else {
            content = `
            <div class="p-4 rounded-xl border border-emerald-300 bg-emerald-50/60">
                <div class="flex items-center gap-2 mb-2">
                    <span class="p-1 rounded-full bg-emerald-500 text-white">
                        <i data-lucide="truck" class="w-4 h-4"></i>
                    </span>
                    <h4 class="font-bold text-emerald-800">ক্যাশ অন ডেলিভারি (Cash on Delivery)</h4>
                </div>
                <p class="text-xs text-slate-600">
                    পণ্যটি হাতে পাওয়ার পর ডেলিভারিম্যানের কাছে সম্পূর্ণ টাকা পরিশোধ করুন। পণ্যটি দেখে বুঝে নেওয়ার সুযোগ রয়েছে।
                </p>
            </div>
            `;
        }

        detailsContainer.innerHTML = content;
        if (window.lucide) lucide.createIcons();
    },

    // Interactive bKash simulation popup
    simulateBkashModal() {
        const modalId = 'bkash-interactive-modal';
        let modal = document.getElementById(modalId);
        if (modal) modal.remove();

        const amount = document.getElementById('checkout-grand-total')?.textContent || '৳1,500';

        const modalDiv = document.createElement('div');
        modalDiv.id = modalId;
        modalDiv.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in';
        modalDiv.innerHTML = `
        <div class="bg-[#e2136e] w-full max-w-sm rounded-2xl overflow-hidden shadow-2xl text-white">
            <div class="p-5 text-center border-b border-pink-400">
                <div class="flex items-center justify-between">
                    <h3 class="font-bold text-lg tracking-wide">bKash Payment</h3>
                    <button onclick="document.getElementById('${modalId}').remove()" class="text-pink-200 hover:text-white">&times;</button>
                </div>
                <p class="text-xs text-pink-100 mt-1">Merchant: BongoBazaar Online Ltd.</p>
                <div class="mt-3 bg-white/20 py-2 px-3 rounded-lg inline-block">
                    <span class="text-xs">Payable Amount:</span>
                    <span class="text-lg font-extrabold ml-1">${amount}</span>
                </div>
            </div>
            <div class="p-5 bg-white text-slate-800 space-y-4">
                <div id="bkash-step-1">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">আপনার বিকাশ একাউন্ট নম্বর দিন:</label>
                    <input type="text" id="bkash-phone-input" placeholder="01XXXXXXXXX" value="01712345678" class="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:ring-2 focus:ring-[#e2136e] outline-none">
                    <p class="text-[11px] text-slate-500 mt-1">আমরা আপনার নম্বরে একটি ৪ ডিজিটের ভেরিফিকেশন ওটিপি পাঠাবো।</p>
                    <button type="button" onclick="PaymentGateway.nextBkashStep(2)" class="w-full mt-4 py-2.5 bg-[#e2136e] hover:bg-pink-700 text-white font-bold rounded-lg text-sm shadow">
                        এগিয়ে যান (CONFIRM)
                    </button>
                </div>
                <div id="bkash-step-2" class="hidden">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ভেরিফিকেশন কোড (OTP) দিন:</label>
                    <input type="text" id="bkash-otp-input" placeholder="1234" value="8492" class="w-full px-3 py-2 border rounded-lg font-mono text-center tracking-widest text-lg font-bold focus:ring-2 focus:ring-[#e2136e] outline-none">
                    <p class="text-[11px] text-emerald-600 mt-1 font-semibold">&bull; ডেমো ওটিপি অটো-ফিল করা হয়েছে: 8492</p>
                    <button type="button" onclick="PaymentGateway.nextBkashStep(3)" class="w-full mt-4 py-2.5 bg-[#e2136e] hover:bg-pink-700 text-white font-bold rounded-lg text-sm shadow">
                        যাচাই করুন
                    </button>
                </div>
                <div id="bkash-step-3" class="hidden">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">বিকাশ পিন (PIN) দিন:</label>
                    <input type="password" id="bkash-pin-input" placeholder="•••••" value="12345" maxlength="5" class="w-full px-3 py-2 border rounded-lg font-mono text-center tracking-widest text-lg font-bold focus:ring-2 focus:ring-[#e2136e] outline-none">
                    <p class="text-[11px] text-slate-400 mt-1 text-center">নিরাপদ ২৫৬-বিট এনক্রিপ্টেড গেটওয়ে</p>
                    <button type="button" onclick="PaymentGateway.completeBkashPayment()" class="w-full mt-4 py-2.5 bg-[#e2136e] hover:bg-pink-700 text-white font-bold rounded-lg text-sm shadow flex items-center justify-center gap-2">
                        <span>পেমেন্ট নিশ্চিত করুন</span>
                    </button>
                </div>
            </div>
            <div class="p-3 bg-pink-100 text-center text-[11px] text-[#e2136e] font-semibold border-t">
                16247 ডায়াল করে বিকাশ হেল্পলাইনে যোগাযোগ করুন
            </div>
        </div>
        `;
        document.body.appendChild(modalDiv);
    },

    nextBkashStep(step) {
        document.getElementById('bkash-step-1')?.classList.add('hidden');
        document.getElementById('bkash-step-2')?.classList.add('hidden');
        document.getElementById('bkash-step-3')?.classList.add('hidden');
        document.getElementById(`bkash-step-${step}`)?.classList.remove('hidden');
    },

    completeBkashPayment() {
        const randTrx = 'BK' + Math.random().toString(36).substring(2, 10).toUpperCase();
        this.verifiedTrxId = randTrx;

        const inputTrx = document.getElementById('bkash-trxid');
        if (inputTrx) inputTrx.value = randTrx;

        document.getElementById('bkash-interactive-modal')?.remove();
        showToast('বিকাশ পেমেন্ট সফল!', `ট্রানজেকশন আইডি: ${randTrx}`, 'success');

        if (this.onSuccessCallback) {
            this.onSuccessCallback(randTrx);
        }
    },

    simulateNagadModal() {
        const randTrx = 'NG' + Math.random().toString(36).substring(2, 10).toUpperCase();
        this.verifiedTrxId = randTrx;

        const inputTrx = document.getElementById('nagad-trxid');
        if (inputTrx) inputTrx.value = randTrx;

        showToast('নগদ ভেরিফাইড!', `ট্রানজেকশন আইডি: ${randTrx} স্বয়ংক্রিয়ভাবে সংযুক্ত হয়েছে`, 'success');
    },

    getTransactionId() {
        if (this.currentMethod === 'bKash') {
            return document.getElementById('bkash-trxid')?.value.trim() || this.verifiedTrxId || 'BKASH-VERIFIED';
        }
        if (this.currentMethod === 'Nagad') {
            return document.getElementById('nagad-trxid')?.value.trim() || this.verifiedTrxId || 'NAGAD-VERIFIED';
        }
        if (this.currentMethod === 'Rocket') {
            return document.getElementById('rocket-trxid')?.value.trim() || 'ROCKET-MANUAL';
        }
        if (this.currentMethod === 'Card') {
            return 'CARD-' + Math.random().toString(36).substring(2, 8).toUpperCase();
        }
        return 'COD';
    }
};

window.PaymentGateway = PaymentGateway;
