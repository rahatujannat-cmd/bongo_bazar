/**
 * BongoBazaar - Payment (Cash on Delivery only)
 *
 * The old fake bKash / Nagad / Rocket / card simulation was removed in
 * the batch-2 security fix: it showed hardcoded OTP/PIN values, fake
 * merchant numbers and random transaction IDs, and pretended a payment
 * had succeeded when no money moved at all. Customers must never be
 * asked to send money to a number shown by this file.
 *
 * Checkout is Cash on Delivery only. A real bKash / Nagad gateway
 * integration (merchant account + server-side verification) is a
 * separate future step - do NOT add any real payment credentials here.
 */

const PaymentGateway = {
    currentMethod: 'COD',
    verifiedTrxId: null,
    onSuccessCallback: null,

    init(onSuccess) {
        this.onSuccessCallback = onSuccess;
    },

    // Kept for compatibility with any page that calls it: COD has no
    // online transaction, so the transaction id is always 'COD'.
    getTransactionId() {
        return 'COD';
    },

    // Removed: simulateBkashModal, simulateNagadModal,
    // completeBkashPayment and all fake TrxID / OTP / PIN code.
};

window.PaymentGateway = PaymentGateway;
