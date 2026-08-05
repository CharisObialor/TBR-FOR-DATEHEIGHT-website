import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const TermsOfService = () => {
  return (
    <div className="bg-white min-h-screen">
      <section className="pt-32 pb-16 bg-slate-950 text-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <Link to="/" className="inline-flex items-center text-sm text-slate-400 hover:text-white mb-6">
            <ArrowLeft size={16} className="mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tighter leading-none mb-4">Terms of Service</h1>
          <p className="text-sm text-slate-400">Last updated: July 2026</p>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 prose prose-slate max-w-none">

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">1. Agreement to Terms</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            By accessing or using the TBR Solutions website (tbrsolutions.ng), client portal (portal.tbrsolutions.ng), or any of our services, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our platform or services.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            These Terms constitute a legally binding agreement between you ("Client", "you", or "your") and TBR Solutions ("we", "us", or "our"), a company registered in Nigeria.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">2. Definitions</h2>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>"Platform"</strong> refers to our website, client portal, and all related applications and services.</li>
            <li><strong>"Services"</strong> refers to the tax, business, regulatory, and advisory services offered by TBR Solutions, as described on our platform.</li>
            <li><strong>"Client Portal"</strong> refers to the secure online portal at portal.tbrsolutions.ng where clients manage their service requests, documents, and payments.</li>
            <li><strong>"Content"</strong> refers to all text, images, data, information, and materials available on our platform.</li>
            <li><strong>"Recurring Services"</strong> refers to services with ongoing billing cycles (monthly, quarterly, or annually) that require periodic payment.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">3. Eligibility</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            Our services are available to individuals and organisations that can form legally binding contracts under applicable laws. By using our platform, you represent that you are at least 18 years of age and have the legal capacity to enter into these Terms.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">4. Account Registration</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            To access the client portal, you must register for an account. You agree to:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li>Provide accurate, current, and complete information during registration.</li>
            <li>Maintain and update your information to keep it accurate and complete.</li>
            <li>Maintain the security and confidentiality of your login credentials.</li>
            <li>Accept responsibility for all activities that occur under your account.</li>
            <li>Notify us immediately of any unauthorised use of your account.</li>
          </ul>
          <p className="text-slate-600 leading-relaxed mb-4">
            We reserve the right to suspend or terminate accounts that are found to contain inaccurate information or that violate these Terms.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">5. Scope of Services</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            TBR Solutions provides professional advisory services in the following areas:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li>Tax advisory, compliance, registration, and filing services.</li>
            <li>Company registration and corporate affairs services (CAC filings).</li>
            <li>Regulatory compliance and advisory services.</li>
            <li>Business advisory and consulting services.</li>
            <li>ESG (Environmental, Social, and Governance) advisory services.</li>
            <li>Payroll management, bookkeeping, and outsourced accounting.</li>
            <li>Risk management and compliance consulting.</li>
            <li>Digital and technology compliance services.</li>
          </ul>
          <p className="text-slate-600 leading-relaxed mb-4">
            The specific scope, deliverables, timelines, and fees for each service engagement will be confirmed in a service agreement or order confirmation shared with you before work begins.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">6. Service Requests and Orders</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>6.1 Requesting Services.</strong> You may request services through the client portal by selecting one or more services, providing required information, and completing payment. Each service request becomes an "order" in our system.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>6.2 Order Review.</strong> After payment, your order will be reviewed by our team. We may contact you for additional information or clarification before commencing work.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>6.3 Service Delivery.</strong> We will endeavour to deliver services within the estimated timelines provided. However, timelines are estimates and may be affected by factors beyond our control, including delays in regulatory processing, incomplete information from the client, or changes in requirements.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>6.4 Service Revisions.</strong> Where a service includes review cycles (e.g., document preparation), the number of included revisions will be specified in the service agreement. Additional revisions may incur extra charges.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">7. Pricing and Payment</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>7.1 Pricing.</strong> Service prices are displayed on the platform as price ranges. The final amount for each service will be confirmed by our team and displayed in your order before payment. Prices are in Nigerian Naira (NGN) and are exclusive of VAT unless stated otherwise.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>7.2 Payment Processing.</strong> All payments are processed through our secure payment gateway, Korapay. We do not store your card details. Payment may be made via debit card, bank transfer, or other methods supported by the gateway.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>7.3 Pay Ahead.</strong> For recurring services, you may pay for up to 24 months in advance. The total amount will be calculated as the base price per billing cycle multiplied by the number of months selected.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>7.4 Refunds.</strong> Refunds are handled on a case-by-case basis. If work has not commenced on your order, you may request a full refund. If work has partially commenced, a partial refund may be issued at our discretion. Refund requests should be submitted through the client portal or by contacting our support team. Korapay refund processing typically takes 5-10 business days.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>7.5 Late Payments.</strong> For recurring services, failure to make payment before the end of your billing period may result in service suspension. We will send you a reminder notification 5 days before your billing period ends.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">8. Recurring Billing</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>8.1 Billing Cycles.</strong> Recurring services are billed on a monthly, quarterly, or annual basis as specified for each service. When you pay ahead for multiple months, your billing period covers the number of months selected at the time of payment.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>8.2 Billing Notifications.</strong> We will send you an email notification 5 days before your current billing period expires. This notification will be sent from <em>billing@tbrsolutions.ng</em>.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>8.3 Renewal.</strong> To continue your recurring service after the current billing period, you must make a new payment through the client portal. Auto-renewal is not enabled by default.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">9. Client Obligations</h2>
          <p className="text-slate-600 leading-relaxed mb-4">You agree to:</p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li>Provide accurate, complete, and timely information required for the delivery of services.</li>
            <li>Respond to our requests for information or clarification within a reasonable time.</li>
            <li>Ensure that documents and information you provide are authentic and lawful.</li>
            <li>Use the platform in compliance with all applicable laws and regulations.</li>
            <li>Not share your account credentials with unauthorised persons.</li>
            <li>Not use the platform for any fraudulent, illegal, or unauthorised purpose.</li>
            <li>Not attempt to gain unauthorised access to any part of the platform or its systems.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">10. Intellectual Property</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>10.1 Our IP.</strong> All content, trademarks, logos, designs, software, and other intellectual property on the platform are owned by or licensed to TBR Solutions. You may not reproduce, distribute, or create derivative works without our express written consent.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>10.2 Client Deliverables.</strong> Upon full payment, you receive the right to use the deliverables produced as part of our services for their intended purpose. We retain the right to use general methodologies, know-how, and insights gained from engagements, provided no client-confidential information is disclosed.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>10.3 Your Content.</strong> You retain ownership of all documents and information you upload to the portal. By providing this information, you grant us a limited licence to use it solely for the purpose of delivering the requested services.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">11. Confidentiality</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            We treat all client information as confidential. We will not disclose your personal data, business information, or documents to third parties except as necessary for service delivery (e.g., submissions to regulatory bodies), as required by law, or with your explicit consent. Our confidentiality obligations survive the termination of our engagement.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">12. Limitation of Liability</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>12.1</strong> To the maximum extent permitted by law, TBR Solutions shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of or related to your use of our platform or services.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>12.2</strong> Our total liability for any claim arising out of or related to these Terms or our services shall not exceed the total fees you paid to us for the specific service giving rise to the claim in the 12 months preceding the claim.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>12.3</strong> We are not liable for delays or failures in performance resulting from causes beyond our reasonable control, including natural disasters, government actions, regulatory changes, internet outages, or force majeure events.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>12.4</strong> Our services do not constitute legal, financial, or investment advice. While we strive to provide accurate and up-to-date information, you should independently verify critical decisions and consult with other qualified professionals as needed.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">13. Indemnification</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            You agree to indemnify and hold harmless TBR Solutions, its directors, employees, and agents from and against any claims, liabilities, damages, losses, and expenses (including legal fees) arising out of or related to your use of the platform, your violation of these Terms, or your provision of inaccurate or unlawful information.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">14. Termination</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>14.1 By You.</strong> You may close your account at any time by contacting our support team. Closure of your account does not relieve you of any obligation to pay outstanding fees.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>14.2 By Us.</strong> We may suspend or terminate your access to the platform if you breach these Terms, engage in fraudulent activity, or if we are required to do so by law. We will provide reasonable notice before termination where practicable.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>14.3 Effect of Termination.</strong> Upon termination, your right to access the platform ceases. We will retain your data in accordance with our Privacy Policy. Any outstanding payments remain due and payable.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">15. Dispute Resolution</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>15.1 Governing Law.</strong> These Terms are governed by and construed in accordance with the laws of the Federal Republic of Nigeria.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>15.2 Negotiation.</strong> In the event of any dispute arising out of or relating to these Terms or our services, the parties shall first attempt to resolve the dispute through good-faith negotiation within 30 days of written notice.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            <strong>15.3 Arbitration.</strong> If the dispute cannot be resolved through negotiation, it shall be submitted to arbitration in Lagos, Nigeria, in accordance with the Arbitration and Mediation Act 2023. The decision of the arbitrator shall be final and binding.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">16. Amendments</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            We reserve the right to modify these Terms at any time. Changes will be posted on this page with an updated "Last updated" date. Material changes will be communicated via email or through the client portal. Your continued use of the platform after changes are posted constitutes your acceptance of the updated Terms.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">17. Severability</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            If any provision of these Terms is found to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">18. Entire Agreement</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            These Terms, together with our Privacy Policy and any specific service agreements, constitute the entire agreement between you and TBR Solutions regarding the use of our platform and services, superseding any prior agreements or understandings.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">19. Contact Us</h2>
          <div className="bg-slate-50 border border-slate-200 p-6 mt-4">
            <p className="text-slate-600 leading-relaxed mb-2"><strong>TBR Solutions</strong></p>
            <p className="text-slate-600 leading-relaxed mb-2">Plot 5A, Block A10, Admiralty Way, Lekki, Lagos, Nigeria</p>
            <p className="text-slate-600 leading-relaxed mb-2">Email: <a href="mailto:info@tbrsolutions.ng" className="text-blue-600 hover:underline">info@tbrsolutions.ng</a></p>
            <p className="text-slate-600 leading-relaxed">Phone: +234 706 834 8923</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default TermsOfService;
