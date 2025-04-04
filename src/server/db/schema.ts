import { relations, sql } from "drizzle-orm";
import {
  index,
  integer,
  jsonb,
  pgTableCreator,
  primaryKey,
  serial,
  text,
  timestamp,
  varchar,
} from "drizzle-orm/pg-core";
import { type AdapterAccount } from "next-auth/adapters";

/**
 * This is an example of how to use the multi-project schema feature of Drizzle ORM. Use the same
 * database instance for multiple projects.
 *
 * @see https://orm.drizzle.team/docs/goodies#multi-project-schema
 */
export const createTable = pgTableCreator((name) => `histocar_${name}`);


export const users = createTable("user", {
  id: varchar("id", { length: 255 })
    .notNull()
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  name: varchar("name", { length: 255 }),
  email: varchar("email", { length: 255 }).notNull(),
  emailVerified: timestamp("email_verified", {
    mode: "date",
    withTimezone: true,
  }).default(sql`CURRENT_TIMESTAMP`),
  image: varchar("image", { length: 255 }),
});

export const usersRelations = relations(users, ({ many }) => ({
  accounts: many(accounts),
}));

export const accounts = createTable(
  "account",
  {
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id),
    type: varchar("type", { length: 255 })
      .$type<AdapterAccount["type"]>()
      .notNull(),
    provider: varchar("provider", { length: 255 }).notNull(),
    providerAccountId: varchar("provider_account_id", {
      length: 255,
    }).notNull(),
    refresh_token: text("refresh_token"),
    access_token: text("access_token"),
    expires_at: integer("expires_at"),
    token_type: varchar("token_type", { length: 255 }),
    scope: varchar("scope", { length: 255 }),
    id_token: text("id_token"),
    session_state: varchar("session_state", { length: 255 }),
  },
  (account) => ({
    compoundKey: primaryKey({
      columns: [account.provider, account.providerAccountId],
    }),
    userIdIdx: index("account_user_id_idx").on(account.userId),
  })
);

export const accountsRelations = relations(accounts, ({ one }) => ({
  user: one(users, { fields: [accounts.userId], references: [users.id] }),
}));

export const sessions = createTable(
  "session",
  {
    sessionToken: varchar("session_token", { length: 255 })
      .notNull()
      .primaryKey(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id),
    expires: timestamp("expires", {
      mode: "date",
      withTimezone: true,
    }).notNull(),
  },
  (session) => ({
    userIdIdx: index("session_user_id_idx").on(session.userId),
  })
);

export const sessionsRelations = relations(sessions, ({ one }) => ({
  user: one(users, { fields: [sessions.userId], references: [users.id] }),
}));

export const verificationTokens = createTable(
  "verification_token",
  {
    identifier: varchar("identifier", { length: 255 }).notNull(),
    token: varchar("token", { length: 255 }).notNull(),
    expires: timestamp("expires", {
      mode: "date",
      withTimezone: true,
    }).notNull(),
  },
  (vt) => ({
    compoundKey: primaryKey({ columns: [vt.identifier, vt.token] }),
  })
);

export const matriculas = createTable(
  "matricula",
  {
    id: serial("id").primaryKey(),
    matricula: varchar("matricula", { length: 255 }).notNull().unique(),
    modelo: varchar("modelo", { length: 255 }).notNull().default(""),

    data: jsonb("data").notNull(),

    createdById: varchar("created_by", { length: 255 })
      .notNull()
      .references(() => users.id),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).$onUpdate(
      () => new Date(),
    ),
  },
  (example) => ({
    matriculaIndex: index("matricula_idx").on(example.matricula),
    createdByIdIdx: index("matricula_created_by_idx").on(example.createdById),
  }),
);

export const matriculasRelations = relations(matriculas, ({ one, many }) => ({
  creator: one(users, { fields: [matriculas.createdById], references: [users.id] }),
  consultations: many(matriculaConsultations),
}));

export const matriculaConsultations = createTable(
  "matricula_consultation",
  {
    id: serial("id").primaryKey(),
    matriculaId: integer("matricula_id")
      .notNull()
      .references(() => matriculas.id),
    consultedById: varchar("consulted_by", { length: 255 })
      .notNull()
      .references(() => users.id),
    consultedAt: timestamp("consulted_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (consultation) => ({
    matriculaIdIdx: index("matricula_consultation_matricula_id_idx").on(consultation.matriculaId),
    consultedByIdIdx: index("matricula_consultation_user_id_idx").on(consultation.consultedById),
    uniqueConsultation: index("unique_matricula_consultation_idx").on(
      consultation.matriculaId, 
      consultation.consultedById
    ),
  }),
);

export const matriculaConsultationsRelations = relations(matriculaConsultations, ({ one }) => ({
  matricula: one(matriculas, { fields: [matriculaConsultations.matriculaId], references: [matriculas.id] }),
  user: one(users, { fields: [matriculaConsultations.consultedById], references: [users.id] }),
}));

export const usersMatriculasRelations = relations(users, ({ many }) => ({
  createdMatriculas: many(matriculas),
  consultedMatriculas: many(matriculaConsultations),
}));
