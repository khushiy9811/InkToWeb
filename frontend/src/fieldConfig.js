export const FIELD_SECTIONS = [
  {
    title: "Form Metadata",
    fields: [
      { name: "branch", label: "Branch" },
      { name: "form_date", label: "Date" },
    ],
  },
  {
    title: "Applicant Details",
    fields: [
      { name: "full_name", label: "Full Name (as per ID)" },
      { name: "father_spouse_name", label: "Father's / Spouse's Name" },
      { name: "date_of_birth", label: "Date of Birth" },
      {
        name: "gender",
        label: "Gender",
        type: "select",
        options: ["male", "female", "other"],
      },
      { name: "nationality", label: "Nationality" },
      { name: "marital_status", label: "Marital Status" },
      { name: "occupation", label: "Occupation" },
      { name: "annual_income", label: "Annual Income (Rs.)" },
    ],
  },
  {
    title: "Contact & Address Details",
    fields: [
      { name: "address_line1", label: "Permanent Address Line 1" },
      { name: "address_line2", label: "Permanent Address Line 2" },
      { name: "city", label: "City" },
      { name: "state", label: "State" },
      { name: "pin_code", label: "PIN Code" },
      { name: "mobile_number", label: "Mobile Number" },
      { name: "email", label: "Email Address" },
    ],
  },
  {
    title: "Identification Details",
    fields: [
      { name: "aadhaar_id_number", label: "Aadhaar / National ID Number" },
      { name: "pan_number", label: "PAN No." },
      { name: "id_proof_type", label: "ID Proof Type" },
    ],
  },
  {
    title: "Account Details",
    fields: [
      {
        name: "account_type",
        label: "Account Type",
        type: "select",
        options: ["savings", "current"],
      },
      { name: "initial_deposit", label: "Initial Deposit (Rs.)" },
    ],
  },
  {
    title: "Nominee Details",
    fields: [
      { name: "nominee_name", label: "Nominee Name" },
      { name: "nominee_relationship", label: "Relationship" },
    ],
  },
  {
    title: "Declaration",
    fields: [
      { name: "place", label: "Place" },
      { name: "signature_date", label: "Date" },
    ],
  },
];

export const ALL_FIELDS = FIELD_SECTIONS.flatMap((s) => s.fields);

export const LOW_CONFIDENCE_THRESHOLD = 65;
