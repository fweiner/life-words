interface PhoneMockupProps {
  children: React.ReactNode;
}

export function PhoneMockup({ children }: PhoneMockupProps) {
  return (
    <div className="promo-phone" aria-hidden="true">
      <div className="promo-phone-chrome">
        <div className="promo-phone-dot bg-red-400" />
        <div className="promo-phone-dot bg-yellow-400" />
        <div className="promo-phone-dot bg-green-400" />
      </div>
      <div className="promo-phone-body">{children}</div>
    </div>
  );
}
