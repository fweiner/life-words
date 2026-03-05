/* eslint-disable @next/next/no-img-element */

const contacts = [
  {
    name: "Sarah",
    relation: "Daughter",
    photo: "/images/sarah.jpg",
  },
  {
    name: "Max",
    relation: "Dog",
    photo: "/images/max.jpg",
  },
  {
    name: "Dr. Chen",
    relation: "Doctor",
    photo: null,
  },
];

export function MockContacts() {
  return (
    <div className="flex flex-col sm:flex-row gap-4 promo-stagger">
      {contacts.map((c) => (
        <div
          key={c.name}
          className={`bg-white rounded-2xl border-2 ${c.photo ? "border-gray-200" : "border-amber-300"} shadow-md p-5 w-full sm:w-48 flex-shrink-0`}
        >
          <div className="flex justify-center mb-3">
            {c.photo ? (
              <img
                src={c.photo}
                alt=""
                className="w-16 h-16 rounded-full object-cover"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white text-2xl font-bold">
                {c.name[0]}
              </div>
            )}
          </div>
          <p className="text-center font-bold text-gray-900">{c.name}</p>
          <p className="text-center text-sm text-gray-500">{c.relation}</p>
          {!c.photo && (
            <p className="text-center text-xs text-amber-600 font-medium mt-2">
              Needs photo
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
