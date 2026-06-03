import { useState } from 'react'
import axios from 'axios'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const PRODUCTS = [
  'Hex Bolts', 'Anchor Bolts', 'Foundation Bolts',
  'Nuts', 'Washers', 'Threaded Rods', 'General Enquiry',
]

function validate({ name, email, phone }) {
  const errors = {}

  const trimmedName = name.trim()
  if (!trimmedName) {
    errors.name = 'Name is required'
  } else if (trimmedName.length < 2) {
    errors.name = 'Name must be at least 2 characters'
  }

  const trimmedEmail = email.trim()
  if (!trimmedEmail) {
    errors.email = 'Email is required'
  } else if (!EMAIL_RE.test(trimmedEmail)) {
    errors.email = 'Enter a valid email'
  }

  const trimmedPhone = phone.trim()
  if (!trimmedPhone) {
    errors.phone = 'Phone is required'
  } else if (/[^\d\s+\-()]/.test(trimmedPhone)) {
    errors.phone = 'Enter a valid phone number'
  } else {
    const digits = trimmedPhone.replace(/\D/g, '')
    if (digits.length < 7 || digits.length > 15) {
      errors.phone = 'Enter a valid phone number'
    }
  }

  return errors
}

const BLANK = { name: '', email: '', phone: '', product: '', message: '' }

export default function ContactForm() {
  const [form, setForm]         = useState(BLANK)
  const [errors, setErrors]     = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [status, setStatus]     = useState(null) // 'success' | 'error'

  const set = (k) => (e) => setForm(prev => ({ ...prev, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()

    const errs = validate(form)
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setSubmitting(true)
    setStatus(null)
    try {
      await axios.post('https://terns-exim-api.onrender.com/submit-lead', {
        name:    form.name.trim(),
        email:   form.email.trim(),
        phone:   form.phone.trim(),
        product: form.product,
        message: form.message,
      })
      setStatus('success')
      setForm(BLANK)
      setErrors({})
    } catch {
      setStatus('error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="contact-page">
      <div className="contact-card">
        <h1 className="contact-title">Product Enquiry</h1>
        <p className="contact-sub">
          Fill in the form and our team will get back to you shortly.
        </p>

        {status === 'success' && (
          <div className="alert alert-success">
            Enquiry submitted successfully. We will contact you shortly.
          </div>
        )}
        {status === 'error' && (
          <div className="alert alert-error">
            Something went wrong. Please try again.
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="contact-form">
          <div className="form-group">
            <label>Name *</label>
            <input
              value={form.name}
              onChange={set('name')}
              placeholder="Your full name"
              className={errors.name ? 'input-error' : ''}
            />
            {errors.name && <span className="field-error">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="email@example.com"
              className={errors.email ? 'input-error' : ''}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label>Phone *</label>
            <input
              value={form.phone}
              onChange={set('phone')}
              placeholder="+91 99999 99999"
              className={errors.phone ? 'input-error' : ''}
            />
            {errors.phone && <span className="field-error">{errors.phone}</span>}
          </div>

          <div className="form-group">
            <label>Product</label>
            <select value={form.product} onChange={set('product')}>
              <option value="">Select product (optional)</option>
              {PRODUCTS.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Message</label>
            <textarea
              value={form.message}
              onChange={set('message')}
              placeholder="Tell us about your requirements..."
              rows={4}
            />
          </div>

          <button type="submit" className="btn-submit" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Send Enquiry'}
          </button>
        </form>
      </div>
    </div>
  )
}
