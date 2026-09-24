import { useTheme } from "@/providers/ThemeProvider";

const IMG = "/img";

const CATEGORIES = [
  {
    title: "IT Development",
    description: "Write real code from day one — backend services, APIs and the tooling teams actually ship with.",
    courses: 120,
    image: "1.jpg",
  },
  {
    title: "Web Design",
    description: "Turn a rough idea into a clean, responsive layout that holds up on every screen size.",
    courses: 70,
    image: "2.jpg",
  },
  {
    title: "Illustration & Drawing",
    description: "Build confidence with line, colour and composition through short, guided drawing exercises.",
    courses: 55,
    image: "3.jpg",
  },
  {
    title: "Social Media",
    description: "Plan content, grow an audience and read the numbers that tell you what is working.",
    courses: 40,
    image: "4.jpg",
  },
  {
    title: "Photoshop",
    description: "Learn retouching, masking and compositing by following each edit step by step.",
    courses: 220,
    image: "5.jpg",
  },
  {
    title: "Cryptocurrencies",
    description: "Understand wallets, blockchains and risk before you put any money on the line.",
    courses: 25,
    image: "6.jpg",
  },
];

const StudentHome = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="student-home">
      <section
        className="student-hero"
        style={{ backgroundImage: `url(${IMG}/bg.jpg)` }}
      >
        <div className="student-container">
          <div className="student-hero__content">
            <h2 className="student-hero__title">
              One of the Best Education Systems
            </h2>

            <p className="student-text student-text--light">
              Discover a modern education system that inspires curiosity, develops
              essential skills, and empowers students to reach their full potential.
              <br className="student-hero__break" />
              Learn from experienced educators, explore new ideas, and build a strong
              foundation for a successful future.
            </p>
          </div>
        </div>
      </section>

      <section className="student-section">
        <div className="student-container">
          <div className="student-section-heading student-categories__heading">
            <h2 className="student-section-heading__title">Our Course Categories</h2>
            <p className="student-text">
              Six areas to start from, each built as a path rather than a pile of videos. Every course begins with the
              basics and ends with something you have made yourself.
            </p>
          </div>

          <div className="student-categories__grid">
            {CATEGORIES.map((category) => (
              <article key={category.title} className="student-category">
                <img className="student-category__thumb" src={`${IMG}/categories/${category.image}`} alt="" />
                <div className="student-category__body">
                  <h5 className="student-category__title">{category.title}</h5>
                  <p className="student-text student-category__text">{category.description}</p>
                  <span className="student-category__count">{category.courses} Courses</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <div className="horizontal-line"></div>

      <section className="student-section">
        <div className="student-container">
          <div className="student-section-heading student-section-heading--accent">
            <h2 className="student-section-heading__title">Learn a Little, Every Day</h2>
            <p className="student-text">
              Life is not measured by how fast we arrive, but by how well we walk. Every lesson learned, every mistake
              forgiven and every small step taken with patience adds up to a person we are proud to become.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default StudentHome;