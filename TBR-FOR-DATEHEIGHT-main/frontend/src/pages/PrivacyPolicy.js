import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const PrivacyPolicy = () => {
  return (
    <div className="bg-white min-h-screen">
      <section className="pt-32 pb-16 bg-slate-950 text-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <Link to="/" className="inline-flex items-center text-sm text-slate-400 hover:text-white mb-6">
            <ArrowLeft size={16} className="mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tighter leading-none mb-4">Privacy Policy</h1>
          <p className="text-sm text-slate-400">Last updated: July 2026</p>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 prose prose-slate max-w-none">

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">1. Introduction</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            TBR Solutions ("we", "us", or "our") is committed to protecting your personal data. This Privacy Policy describes why and how we collect, use, and share personal data about individuals who visit our website, use our portal, or engage our professional services. It also provides information about your rights under applicable data protection laws, including the Nigeria Data Protection Act 2023 (NDPA).
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            By accessing our website at tbrsolutions.ng, using our client portal at portal.tbrsolutions.ng, or engaging our services, you acknowledge that you have read and understood this Privacy Policy.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">2. Data Controller</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            TBR Solutions, located at Plot 5A, Block A10, Admiralty Way, Lekki, Lagos, Nigeria, is the data controller responsible for your personal data. If you have questions about this policy or our data practices, you may contact us at <strong>info@tbrsolutions.ng</strong> or <strong>+234 706 834 8923</strong>.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">3. Information We Collect</h2>
          <p className="text-slate-600 leading-relaxed mb-4">We may collect and process the following categories of personal data:</p>

          <h3 className="text-lg font-semibold text-slate-900 mt-6 mb-3">3.1 Information You Provide Directly</h3>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Account Information:</strong> Full name, email address, phone number, company name, RC number, and password when you register for our portal.</li>
            <li><strong>Contact Form Submissions:</strong> Name, email address, phone number, subject, and message content when you use our contact form.</li>
            <li><strong>Service Request Data:</strong> Company details, contact person information, and any documents or information you upload when requesting our services.</li>
            <li><strong>Payment Information:</strong> Transaction details including payment references, amounts, and payment method information. (Note: Card details are processed by our payment gateway, Korapay, and are not stored on our servers.)</li>
            <li><strong>Communications:</strong> Any information you provide when you contact our support team, submit a ticket, or correspond with us.</li>
          </ul>

          <h3 className="text-lg font-semibold text-slate-900 mt-6 mb-3">3.2 Information Collected Automatically</h3>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Device Information:</strong> Browser type, operating system, device type, and screen resolution.</li>
            <li><strong>Usage Data:</strong> Pages visited, time spent on pages, navigation paths, and interaction patterns within our portal.</li>
            <li><strong>Log Data:</strong> IP address, access times, referring URLs, and error logs.</li>
            <li><strong>Cookies:</strong> We use essential cookies to maintain your session and preferences. We may also use analytics cookies with your consent to understand how our platform is used.</li>
          </ul>

          <h3 className="text-lg font-semibold text-slate-900 mt-6 mb-3">3.3 Information from Third Parties</h3>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Authentication Providers:</strong> If you register using Google OAuth, we receive your name and email address from Google.</li>
            <li><strong>Payment Processors:</strong> Transaction confirmation and status from Korapay.</li>
            <li><strong>Corporate Clients:</strong> Information about employees or representatives of organisations that engage our services.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">4. How We Use Your Information</h2>
          <p className="text-slate-600 leading-relaxed mb-4">We process your personal data for the following purposes:</p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Service Delivery:</strong> To provide, manage, and deliver the professional services you have engaged us for, including tax compliance, company registration, regulatory filings, and other advisory services.</li>
            <li><strong>Account Management:</strong> To create and manage your portal account, authenticate your identity, and provide customer support.</li>
            <li><strong>Payment Processing:</strong> To process payments, maintain transaction records, and manage billing, including recurring billing for subscription services.</li>
            <li><strong>Communication:</strong> To send service updates, billing reminders, payment confirmations, ticket notifications, and other service-related communications.</li>
            <li><strong>Marketing:</strong> To send you information about our services, events, and insights that may interest you, where you have consented to receive such communications. You may opt out at any time.</li>
            <li><strong>Legal Compliance:</strong> To comply with applicable laws, regulations, and professional obligations, including those imposed by the Federal Inland Revenue Service (FIRS), Corporate Affairs Commission (CAC), and other regulatory bodies.</li>
            <li><strong>Platform Improvement:</strong> To analyse usage patterns, improve our platform functionality, and enhance user experience.</li>
            <li><strong>Security:</strong> To protect our platform, detect fraud, prevent abuse, and ensure the security of our systems and data.</li>
            <li><strong>Dispute Resolution:</strong> To establish, exercise, or defend legal claims where necessary.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">5. Legal Basis for Processing</h2>
          <p className="text-slate-600 leading-relaxed mb-4">We process your personal data based on one or more of the following legal grounds:</p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Contractual Necessity:</strong> Processing is necessary to perform our contract with you or to take steps at your request before entering into a contract.</li>
            <li><strong>Legitimate Interests:</strong> Processing is necessary for our legitimate interests (or those of a third party), provided those interests are not overridden by your rights.</li>
            <li><strong>Consent:</strong> Where you have given us specific consent to process your data for a particular purpose (e.g., marketing communications).</li>
            <li><strong>Legal Obligation:</strong> Processing is necessary to comply with a legal or regulatory obligation to which we are subject.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">6. Data Sharing and Transfers</h2>
          <p className="text-slate-600 leading-relaxed mb-4">We may share your personal data with the following categories of recipients:</p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Regulatory Authorities:</strong> FIRS, CAC, State IRS, and other government agencies as required for service delivery and compliance.</li>
            <li><strong>Payment Processors:</strong> Korapay, for payment processing and verification.</li>
            <li><strong>Service Providers:</strong> Third-party providers who support our operations, including cloud hosting (MongoDB Atlas), email delivery, and analytics services. These providers are contractually bound to protect your data.</li>
            <li><strong>Professional Advisers:</strong> Lawyers, auditors, and consultants as necessary in connection with the services we provide.</li>
            <li><strong>Law Enforcement:</strong> Where required by law, regulation, or court order.</li>
          </ul>
          <p className="text-slate-600 leading-relaxed mb-4">
            Where we transfer personal data outside Nigeria, we ensure appropriate safeguards are in place, including standard contractual clauses and other mechanisms required by the NDPA.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">7. Data Retention</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            We retain your personal data only for as long as necessary to fulfil the purposes for which it was collected, including to satisfy any legal, regulatory, accounting, or reporting requirements. Specific retention periods include:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Account Data:</strong> Retained for the duration of your account and for 6 years after account closure.</li>
            <li><strong>Transaction Records:</strong> Retained for 7 years in accordance with Nigerian tax and corporate law requirements.</li>
            <li><strong>Service Engagement Data:</strong> Retained for 10 years in line with professional record-keeping obligations.</li>
            <li><strong>Contact Form Submissions:</strong> Retained for 2 years from the date of submission.</li>
            <li><strong>Marketing Preferences:</strong> Retained until you withdraw consent or opt out.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">8. Data Security</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            We take the security of your data very seriously. We implement appropriate technical and organisational measures to protect your personal data against unauthorised access, alteration, disclosure, or destruction. These measures include:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li>Encryption of data in transit (TLS/SSL) and at rest.</li>
            <li>Regular security assessments and vulnerability testing.</li>
            <li>Access controls and authentication mechanisms.</li>
            <li>Staff training on data protection and confidentiality.</li>
            <li>Incident response procedures for data breaches.</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">9. Your Rights</h2>
          <p className="text-slate-600 leading-relaxed mb-4">Under the NDPA and other applicable laws, you have the following rights:</p>
          <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-4">
            <li><strong>Right of Access:</strong> To obtain confirmation of whether we process your data and receive a copy of your personal data.</li>
            <li><strong>Right to Rectification:</strong> To have inaccurate personal data corrected and incomplete data completed.</li>
            <li><strong>Right to Erasure:</strong> To request deletion of your personal data where it is no longer necessary, where consent is withdrawn, or where processing is unlawful.</li>
            <li><strong>Right to Restrict Processing:</strong> To request limitation of processing in certain circumstances.</li>
            <li><strong>Right to Data Portability:</strong> To receive your data in a structured, commonly used, machine-readable format and to transmit it to another controller.</li>
            <li><strong>Right to Object:</strong> To object to processing based on legitimate interests or for direct marketing purposes.</li>
            <li><strong>Right to Withdraw Consent:</strong> To withdraw consent at any time where processing is based on consent.</li>
            <li><strong>Right to Lodge a Complaint:</strong> To file a complaint with the Nigeria Data Protection Commission (NDPC) if you believe your rights have been violated.</li>
          </ul>
          <p className="text-slate-600 leading-relaxed mb-4">
            To exercise any of these rights, please contact us at <strong>info@tbrsolutions.ng</strong>.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">10. Cookies and Tracking</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            Our website and portal use cookies and similar technologies. Essential cookies are necessary for the platform to function and do not require consent. Analytics and preference cookies are used only with your consent through our cookie consent mechanism. You can manage your cookie preferences at any time through your browser settings or our cookie consent banner.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">11. Third-Party Links</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            Our website may contain links to third-party websites. We are not responsible for the privacy practices or content of these external sites. We encourage you to review the privacy policy of any third-party site you visit.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">12. Children's Privacy</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            Our services are not directed at individuals under the age of 18. We do not knowingly collect personal data from children. If we become aware that we have collected personal data from a child, we will take steps to delete it promptly.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">13. Changes to This Policy</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            We may update this Privacy Policy from time to time. When we make changes, we will update the "Last updated" date at the top of this page and, where appropriate, notify you by email or through our portal. We encourage you to review this policy periodically.
          </p>

          <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">14. Contact Us</h2>
          <div className="bg-slate-50 border border-slate-200 p-6 mt-4">
            <p className="text-slate-600 leading-relaxed mb-2"><strong>TBR Solutions</strong></p>
            <p className="text-slate-600 leading-relaxed mb-2">Plot 5A, Block A10, Admiralty Way, Lekki, Lagos, Nigeria</p>
            <p className="text-slate-600 leading-relaxed mb-2">Email: <a href="mailto:info@tbrsolutions.ng" className="text-blue-600 hover:underline">info@tbrsolutions.ng</a></p>
            <p className="text-slate-600 leading-relaxed">Phone: +234 706 834 8923</p>
          </div>

          <p className="text-sm text-slate-400 mt-12">
            This Privacy Policy is in compliance with the Nigeria Data Protection Act 2023 (NDPA).
          </p>
        </div>
      </section>
    </div>
  );
};

export default PrivacyPolicy;
