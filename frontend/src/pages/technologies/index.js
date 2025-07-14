import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Backend:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Python — основной язык программирования.
              </li>
              <li className={styles.textItem}>
                Django — фреймворк для разработки веб-приложений.
              </li>
              <li className={styles.textItem}>
                Django REST Framework — библиотека для создания RESTful API.
              </li>
              <li className={styles.textItem}>
                Djoser — библиотека для управления аутентификацией пользователей через REST API.
              </li>
              <li className={styles.textItem}>
                Gunicorn — WSGI HTTP сервер для запуска приложения Django.
              </li>
            </ul>
          </div>
          <h2 className={styles.subtitle}>Frontend:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                React — фреймворк для создания одностраничных приложений (SPA).
              </li>
            </ul>
          </div>
          <h2 className={styles.subtitle}>Инфраструктура и развертывание:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Docker — контейнеризация приложения (отдельные контейнеры для backend, frontend и nginx).
              </li>
              <li className={styles.textItem}>
                Nginx — веб-сервер и обратный прокси для управления запросами.
              </li>
              <li className={styles.textItem}>
                PostgreSQL — реляционная база данных.
              </li>
            </ul>
          </div>
          <h2 className={styles.subtitle}>CI/CD и автоматизация:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                GitHub Actions — автоматизация процессов тестирования и деплоя (CI/CD).
              </li>
              <li className={styles.textItem}>
                Ubuntu — операционная система сервера для развертывания приложения.
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

